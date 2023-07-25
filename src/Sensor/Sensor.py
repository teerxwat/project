import paho.mqtt.client as mqtt

# MQTT broker details
mqtt_broker = "server-mqtt.thddns.net"
mqtt_port = 3333
mqtt_username = "mqtt"
mqtt_password = "admin1234"
mqtt_topic = "sensor/detect"

# Flag to keep track of file operation
file_operation_active = False
previous_file_operation = None


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    global file_operation_active, previous_file_operation

    if msg.topic == mqtt_topic:
        sensor_value = int(msg.payload)
        print("Sensor Value:", sensor_value)

        if sensor_value == 1:
            if not file_operation_active:
                # Publish value 1 to control topic
                client.publish("Control/FaceRecognition", "1")
                # print("Published value 1 to Control/FaceRecognition topic")
                file_operation_active = True
        elif sensor_value == 0:
            if file_operation_active:
                # Publish value 0 to control topic
                client.publish("Control/FaceRecognition", "0")
                # print("Published value 0 to Control/FaceRecognition topic")
                file_operation_active = False

        # Store the current file operation
        previous_file_operation = sensor_value


def connect_to_mqtt_broker():
    client = mqtt.Client()
    client.username_pw_set(mqtt_username, mqtt_password)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(mqtt_broker, mqtt_port, 60)

    client.loop_forever()


# Call the function to connect to the MQTT broker and start listening
connect_to_mqtt_broker()
