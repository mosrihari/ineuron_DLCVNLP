import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array

class PredictImages:

    def __init__(self, images):
        self.images = images
        self.model = None

    def model_load(self):
        return load_model("conv.h5")

    def predict(self):
        img = img_to_array(self.images)
        img = np.expand_dims(img, axis=0)
        self.model = self.model_load()
        preds = self.model.predict(img)

        if preds[0][0] == 1:
            prediction = "Bumrah"
            return [{"image": prediction}]
        elif preds[0][1] == 1:
            prediction = "Dhoni"
            return [{"image": prediction}]
        else:
            prediction = "Kohli"
            return [{"image": prediction}]
