import cv2
import random
import time
import mediapipe as mp
import numpy as np
import pygame 


# Initialize pygame mixer
pygame.mixer.init()

# Load sounds
background_music = "background_music.mp3"
win_sound = "win_sound.wav"
lose_sound = "lose_sound.wav"

# Start playing background music on loop
pygame.mixer.music.load(background_music)
pygame.mixer.music.play(-1)  # -1 means it will loop indefinitely

# Initialize MediaPipe Hands and OpenCV
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)

# Game variables
choices = ["rock", "paper", "scissors"]
score = {"player": 0, "computer": 0}
game_started = False
loading_screen = False  # Flag for loading screen

# Function to detect gesture
def get_gesture(landmarks):
    thumb_tip = landmarks[4].y
    index_tip = landmarks[8].y
    middle_tip = landmarks[12].y
    ring_tip = landmarks[16].y
    pinky_tip = landmarks[20].y

    if all(finger > thumb_tip for finger in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "rock"
    elif all(finger < thumb_tip for finger in [index_tip, middle_tip, ring_tip, pinky_tip]):
        return "paper"
    elif index_tip < thumb_tip and middle_tip < thumb_tip and ring_tip > thumb_tip and pinky_tip > thumb_tip:
        return "scissors"
    return None

# Function to get computer's move
def get_computer_move():
    return random.choice(choices)

#Add the play_sound function
def play_sound(sound_file):
    pygame.mixer.Sound(sound_file).play()

# Function to reset the game
def reset_game():
    global score, game_started, loading_screen
    score = {"player": 0, "computer": 0}
    game_started = False
    loading_screen = False

# Function for the loading animation
def show_loading_animation_with_video(video_path, duration=2, fps=30):
    cap = cv2.VideoCapture(video_path)
    start_time = time.time()

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video if it ends
            continue
        
        # Resize frame to full screen resolution
        frame = cv2.resize(frame, (1920, 1080))  # Change to your screen resolution
        cv2.putText(frame, "Loading...", (800, 600), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.imshow("Stone Paper Scissors", frame)

        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break

def blink_text(frame, text, position, duration=2, blink_rate=0.5):
    start_time = time.time()
    while time.time() - start_time < duration:
        # Show text
        frame_with_text = frame.copy()
        cv2.putText(frame_with_text, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
        cv2.imshow("Stone Paper Scissors", frame_with_text)
        if cv2.waitKey(int(blink_rate * 1000)) & 0xFF == ord('q'):
            break

        # Hide text
        cv2.imshow("Stone Paper Scissors", frame)
        if cv2.waitKey(int(blink_rate * 1000)) & 0xFF == ord('q'):
            break
# Define the dimensions of the detection area
ROI_WIDTH = 600  # Width of the detection area
ROI_HEIGHT = 400  # Height of the detection area

# Calculate the top-left and bottom-right coordinates to center the ROI
ROI_TOP_LEFT = ((1280 - ROI_WIDTH) // 2, (720 - ROI_HEIGHT) // 2)  # Centered position
ROI_BOTTOM_RIGHT = (ROI_TOP_LEFT[0] + ROI_WIDTH, ROI_TOP_LEFT[1] + ROI_HEIGHT)

def is_within_roi(landmarks):
    # Check if the hand landmarks are within the defined ROI
    for landmark in landmarks:
        x = landmark.x * frame.shape[1]  # Convert normalized coordinates to pixel values
        y = landmark.y * frame.shape[0]
        if not (ROI_TOP_LEFT[0] < x < ROI_BOTTOM_RIGHT[0] and ROI_TOP_LEFT[1] < y < ROI_BOTTOM_RIGHT[1]):
            return False
    return True
def highlight_gesture(frame, landmarks, gesture):

    # Highlight the fingers based on the recognized gesture
    if gesture == "rock":
        # Draw a circle around the thumb and index finger
        thumb_coords = (int(landmarks[4].x * frame.shape[1]), int(landmarks[4].y * frame.shape[0]))
        index_coords = (int(landmarks[8].x * frame.shape[1]), int(landmarks[8].y * frame.shape[0]))
        cv2.circle(frame, thumb_coords, 20, (0, 255, 0), 2)
        cv2.circle(frame, index_coords, 20, (0, 255, 0), 2)
    elif gesture == "paper":
        # Highlight all fingers
        for i in [4, 8, 12, 16, 20]:  # Thumb and all fingertips
            finger_coords = (int(landmarks[i].x * frame.shape[1]), int(landmarks[i].y * frame.shape[0]))
            cv2.circle(frame, finger_coords, 20, (0, 0, 255), 2)
    elif gesture == "scissors":
        # Highlight index and middle fingers
        for i in [8, 12]:  # Index and middle fingers
            finger_coords = (int(landmarks[i].x * frame.shape[1]), int(landmarks[i].y * frame.shape[0]))
            cv2.circle(frame, finger_coords, 20, (255, 0, 0), 2)

# Capture webcam input
cap = cv2.VideoCapture(0)

# Set the window to a specific size
cv2.namedWindow("Stone Paper Scissors", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Stone Paper Scissors", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Load the background image
background_image = cv2.imread('background_image.jpg')
background_image = cv2.resize(background_image, (1280, 720), interpolation=cv2.INTER_LINEAR)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame to mirror the player's movements
    frame = cv2.flip(frame, 1)

    # Draw the ROI rectangle on the frame
    cv2.rectangle(frame, ROI_TOP_LEFT, ROI_BOTTOM_RIGHT, (255, 0, 0), 2)

    if not game_started and not loading_screen:
        # Display start menu with background
        frame[:] = background_image
        cv2.putText(frame, "[ROCK] [PAPER] [SCISSORS]", (200, 250), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3)
        cv2.putText(frame, "Press S to Start", (500, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, "Press R to Reset", (500, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, "Press Q to Exit", (500, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            loading_screen = True  # Start loading screen
        elif key == ord('r'):
            reset_game()
        elif key == ord('q'):
            break

    elif loading_screen:
        # Loading animation code remains unchanged
        show_loading_animation_with_video('loading_video.mp4', duration=10)
        game_started = True
        loading_screen = False  # End loading screen

    else:
        # Game logic when the game has started
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        player_move = None
        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            if is_within_roi(hand_landmarks.landmark):  # Check if landmarks are within ROI
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                player_move = get_gesture(hand_landmarks.landmark)
        if player_move:
            highlight_gesture(frame, hand_landmarks.landmark, player_move)  # Call the highlighting function

            computer_move = get_computer_move()

            # Display recognized gesture
            cv2.putText(frame, f"You played: {player_move}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        if player_move:
            computer_move = get_computer_move()

            if player_move == computer_move:
                result_text = "It's a tie!"
            elif (player_move == "rock" and computer_move == "scissors") or \
                 (player_move == "scissors" and computer_move == "paper") or \
                 (player_move == "paper" and computer_move == "rock"):
                result_text = "You win!"
                score["player"] += 1
            else:
                result_text = "Computer wins!"
                score["computer"] += 1

            cv2.putText(frame, f"Your Move: {player_move}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(frame, f"Computer's Move: {computer_move}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            cv2.putText(frame, result_text, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Score: Player {score['player']} - Computer {score['computer']}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if score["player"] == 5:
                play_sound(win_sound)
                # Blink text for win feedback
                blink_text(frame, "You win the game!", (550, 400), duration=3, blink_rate=0.5)
    
                # Calculate text size
                text = "You win the game!"
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 1
                thickness = 2
                text_size = cv2.getTextSize(text, font, scale, thickness)[0]

                # Calculate centered position
                x = (frame.shape[1] - text_size[0]) // 2  # Center horizontally
                y = (frame.shape[0] + text_size[1]) // 2  # Center vertically

                # Display centered text
                cv2.putText(frame, text, (x, y), font, scale, (255, 255, 255), thickness)
                cv2.imshow("Stone Paper Scissors", frame)
                cv2.waitKey(3000)
                reset_game()

            elif score["computer"] == 5:
                play_sound(lose_sound)
                # Blink text for lose feedback
                blink_text(frame, "Computer wins the game!", (550, 400), duration=3, blink_rate=0.5)

                # Calculate text size
                text = "Computer wins the game!"
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 1
                thickness = 2
                text_size = cv2.getTextSize(text, font, scale, thickness)[0]

                # Calculate centered position
                x = (frame.shape[1] - text_size[0]) // 2  # Center horizontally
                y = (frame.shape[0] + text_size[1]) // 2  # Center vertically

                # Display centered text
                cv2.putText(frame, text, (x, y), font, scale, (255, 255, 255), thickness)
                cv2.imshow("Stone Paper Scissors", frame)
                cv2.waitKey(3000)
                reset_game()


            # 3-second countdown before next round
            for countdown in range(3, 0, -1):
                frame_copy = frame.copy()
                cv2.putText(frame_copy, f"Next round in: {countdown}", (550, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, ), 3)
                cv2.imshow("Stone Paper Scissors", frame_copy)
                cv2.waitKey(1000)  # Wait 1 second

        # Display reset button prompt
        cv2.putText(frame, "Press R to Reset Game", (10, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (250, 250, 0), 2)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            reset_game()

    # Display the frame
    cv2.imshow("Stone Paper Scissors", frame)


cap.release()
cv2.destroyAllWindows()
hands.close()
