#!/usr/bin/env python3
import smach
import rospy
import random
import json
from collections import Counter

MOCK_ORDER = ["cup", "cup"]
class TakeOrder(smach.State):
    
    def __init__(self, context):
        smach.State.__init__(self, outcomes=['done'])
        self.context = context

    def listen(self):
        resp = self.speech()
        if not resp.success:
            self.context.voice_controller.sync_tts("Sorry, I didn't get that")
            return self.listen()
        resp = json.loads(resp.json_response)
        rospy.loginfo(resp)
        return resp

    def get_order(self):
        resp = self.listen()
        if resp["intent"]["name"] != "make_order":
            self.context.voice_controller.sync_tts("Sorry, I didn't get that")
            return self.get_order()
        items = resp["entities"].get("item", [])
        if not items:
            self.context.voice_controller.sync_tts("Sorry, I didn't get that")
            return self.get_order()
        quantities = resp["entities"].get("quantity", [])
        quantified_items = []
        if len(items) == len(quantities) == 1:
            quantified_items.append((int(quantities[0]["value"]), items[0]["value"]))
        else:
            for item in items:
                quantified = False
                for quantity in quantities:
                    if quantity["end"] == item["start"] - 1:
                        quantified_items.append((int(quantity["value"]), item["value"]))
                        quantified = True
                        break
                if not quantified:
                    quantified_items.append((1, item["value"]))
        items = []
        for quantity, item in quantified_items:
            items.extend([item]*quantity)
        items_string = ', '.join([f"{count} {item if count == 1 else item+'s'}" for item, count in Counter(items).items()]).replace(', ', ', and ', len(items)-2)

        self.context.voice_controller.sync_tts(f"You asked for {items_string}, is that correct? Please answer yes or no")
        if not self.affirm():
            self.context.voice_controller.sync_tts("Okay, could you repeat please?")
            return self.get_order()
        return items

    def affirm(self):
        resp = self.listen()
        if resp["intent"]["name"] != "affirm":
            self.context.voice_controller.sync_tts("Sorry, I didn't get that")
            return self.affirm()
        choices = resp["entities"].get("choice", None)
        if choices is None:
            self.context.voice_controller.sync_tts("Sorry, I didn't get that")
            return self.affirm()
        choice = choices[0]["value"].lower()
        if choice not in ["yes", "no"]:
            self.context.voice_controller.sync_tts("Sorry, I didn't get that")
            return self.affirm()
        return choice == "yes"

    def execute(self, userdata):
        self.context.voice_controller.sync_tts("Can I please take your order, please answer after the beep?")
        order = []
        while True:
            order.extend(self.get_order())
            self.context.voice_controller.sync_tts("Can I get you anything else? Please answer yes or no")
            if not self.affirm():
                break
            self.context.voice_controller.sync_tts("What else can I get for you?")
        order_string = ', '.join([f"{count} {item if count == 1 else item+'s'}" for item, count in Counter(order).items()]).replace(', ', ', and ', len(order)-2)

        self.context.voice_controller.sync_tts(f"Your order is {order_string}")
        rospy.set_param(f"/tables/{rospy.get_param('/current_table')}/order", order)
        return 'done'
