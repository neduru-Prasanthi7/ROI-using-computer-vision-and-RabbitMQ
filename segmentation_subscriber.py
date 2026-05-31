import os
import sys
import cv2
import json
import pika
import torch
import base64
import numpy as np

from logging_code import setup_logging

logger = setup_logging("YOLO_SEGMENTATION")

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

YOLO_SEG_PATH = os.path.join(
    BASE_DIR,
    "yolov7_seg"
)

sys.path.insert(0, YOLO_SEG_PATH)

SEGMENT_UTILS_PATH = os.path.join(
    YOLO_SEG_PATH,
    "utils",
    "segment"
)

sys.path.insert(0, SEGMENT_UTILS_PATH)


from models.experimental import attempt_load
from utils.general import non_max_suppression
from general import process_mask


class YOLOv7Segmentor:
    def __init__(self):
        self.device = "cpu"
        self.model = None
        self.connection = None
        self.channel = None
        self.queue_name = "person_queue"
        self.load_model()
        self.connect_rabbitmq()

    def load_model(self):
        try:
            logger.info("LOADING SEGMENTATION MODEL...")
            model_path = os.path.join(BASE_DIR,"yolov7_seg","yolov7-seg.pt")

            logger.info(f"MODEL PATH = {model_path}")
            self.model = attempt_load(model_path,self.device)
            self.model.eval()

            logger.info("SEGMENTATION MODEL LOADED")
        except Exception as e:
            logger.error(f"MODEL LOAD ERROR : {str(e)}")

    def connect_rabbitmq(self):

        try:

            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name,durable=True)

            self.channel.basic_qos(prefetch_count=1)

            logger.info(f"CONNECTED TO {self.queue_name}")

        except Exception as e:
            logger.error(f"RABBITMQ CONNECTION ERROR : {str(e)}")


    def decode_frame(self, frame_data):

        img = base64.b64decode(frame_data)
        np_arr = np.frombuffer(img,dtype=np.uint8)
        frame = cv2.imdecode(np_arr,cv2.IMREAD_COLOR)
        return frame

    def preprocess(self, frame):

        img = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        img = cv2.resize(img,(640, 640))
        img_tensor = torch.from_numpy(img).to(self.device)
        img_tensor = (img_tensor.permute(2, 0, 1).float() / 255.0)
        img_tensor = img_tensor.unsqueeze(0)
        return img_tensor

    def apply_segmentation(self,original,pred,proto,img_tensor):
        if len(pred[0]) == 0:
            return original
        det = pred[0]
        if det.shape[1] < 7:
            return original

        masks = process_mask(proto,det[:, 6:],det[:, :4],img_tensor.shape[2:],upsample=True)
        for mask in masks:
            mask = mask.cpu().numpy()
            mask = cv2.resize(mask,(original.shape[1],original.shape[0]))
            colored_mask = np.zeros_like(original)
            colored_mask[:, :, 1] = (mask > 0.5) * 255

            original = cv2.addWeighted(original,1,colored_mask,0.5,0)
        return original

    def callback(self,ch,method,properties,body):

        try:
            data = json.loads(body)
            cam_name = data["camera_name"]
            frame = self.decode_frame(data["frame"])
            if frame is None:
                return
            original = frame.copy()
            img_tensor = self.preprocess(frame)

            with torch.no_grad():
                outputs = self.model(img_tensor)
            pred = outputs[0]
            proto = outputs[1][-1][0]
            pred = non_max_suppression(pred,0.25,0.45,classes=[0],nm=32)
            original = self.apply_segmentation(original,pred,proto,img_tensor)

            cv2.namedWindow(cam_name,cv2.WINDOW_NORMAL)
            cv2.resizeWindow(cam_name,500,400)
            cv2.imshow(cam_name,original)
            cv2.waitKey(1)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:

            logger.error(f"SEGMENTATION CALLBACK ERROR : {str(e)}")


    def start(self):
        self.channel.basic_consume(queue=self.queue_name,on_message_callback=self.callback,auto_ack=False)
        logger.info("WAITING FOR SEGMENTATION FRAMES...")
        self.channel.start_consuming()


if __name__ == "__main__":

    segmentor = YOLOv7Segmentor()

    segmentor.start()
