import numpy as np
import json
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
import random
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split

# Download required NLTK data
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

try:
    # Load the intents file
    with open('intents.json', 'r', encoding='utf-8') as file:
        intents = json.load(file)
except FileNotFoundError:
    print("Error: intents.json file not found in the current directory")
    exit(1)

# Initialize empty lists
words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

# Process intents
print("Processing intents...")
for intent in intents['intents']:
    for pattern in intent['patterns']:
        try:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])
        except Exception as e:
            print(f"Error processing pattern: {pattern}")
            print(f"Error message: {str(e)}")
            continue

print("Lemmatizing words...")
words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(set(words))
classes = sorted(set(classes))

print(f"Total unique words: {len(words)}")
print(f"Total classes: {len(classes)}")

# Save words and classes
print("Saving words and classes...")
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Prepare training data
print("Preparing training data...")
training = []
output_empty = [0] * len(classes)

for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)
    
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])

print("Shuffling and preparing final training data...")
random.shuffle(training)
training = np.array(training, dtype=object)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

# Create and train the model
print("Creating enhanced neural network model...")
model = Sequential([
    Dense(256, input_shape=(len(train_x[0]),), activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(len(train_y[0]), activation='softmax')
])

# Use a better optimizer configuration
optimizer = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', 
             optimizer=optimizer, 
             metrics=['accuracy'])

# Add callbacks for better training
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=0.0001
    )
]

# Split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(
    np.array(train_x), 
    np.array(train_y), 
    test_size=0.2, 
    random_state=42
)

# Train with validation and callbacks
print("Training the enhanced model...")
history = model.fit(
    X_train, y_train,
    epochs=500,
    batch_size=32,
    validation_data=(X_val, y_val),
    callbacks=callbacks,
    verbose=1
)

# Save the model
model.save('chatbot_model.h5')
print("Enhanced model trained and saved successfully!")

# Plot training history
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'])

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'])

plt.tight_layout()
plt.savefig('training_history.png')
print("Training history plot saved as 'training_history.png'")
