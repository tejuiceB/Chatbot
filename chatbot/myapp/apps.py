from django.apps import AppConfig
import tensorflow as tf

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Initialize TensorFlow model
        try:
            tf.keras.backend.clear_session()
            # Add any model loading code here if needed
            print("TensorFlow initialized successfully")
        except Exception as e:
            print(f"Error initializing TensorFlow: {e}")
