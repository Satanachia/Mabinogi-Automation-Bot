import cv2
import numpy as np
import pyautogui
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
import time

from directkeys import PressKey, ReleaseKey, W, A, S, D, SHIFT, CTRL, ESC, C
from PIL import ImageGrab

class SquireBot:
    
    def __init__(self):
        self.ir_factor = 4
        print("Initialized")
        
    def execute_action_on_squires(self, start, num_chars, action, **kwargs):
        self.alt_tab()
        for i in range(start, num_chars):
            kwargs['squire_id'] = i
            self._select_character(i)
            self._login()
            action(**kwargs)
            self._logout()
        self.alt_tab()
        print("Finished")
        
    def _train_advanced_squire(self, missions_by_id, squire_id, **kwargs):
        self._reassign_missions(missions_by_id, squire_id, number=2)
        self._reset_char_screen()
        self._enter_avalon_gate()
        self._mabi_zoom(12, -500)
        self._move_to_squire("kanna")
        self._end_training()
        self._converse_with_squire()
        self._start_training(3)
        time.sleep(2)
    
    def _enter_avalon_gate(self):
        self._mabi_click(640, 290, delay=0.1)
        self._mabi_click(950, 330, delay=0.5)
        avalon_confirm = "./confirms/avalon_confirm.png"
        self._wait_for_element_or_timeout(avalon_confirm, 0.07, 15)
        time.sleep(2)
        
    def _move_to_squire(self, squire):
        if squire == "kanna":
            self._mabi_click(500, 400, delay=5)
    
    def _converse_with_squire(self):
        self._talk_to_squire()
        for i in range(3):
            self._click_through_text()
            self._answer_conv_question()
            self._end_conv()
    
    def _talk_to_squire(self):
        self._mabi_click(540, 960, delay=0.1)
        PressKey(CTRL)
        self._mabi_click(540, 960, delay=5)
        ReleaseKey(CTRL)
        
        screen_text = self._get_screen_tesseract_text(950, 450, 1000, 900)
        while 'Conversation' not in screen_text and 'Counsel' not in screen_text:
            self._mabi_click(980, 530, delay=0.5)
            screen_text = self._get_screen_tesseract_text(950, 450, 1000, 900)
        
    def _click_through_text(self):
        start_time = time.time()
        conv_confirm = "./confirms/conv_confirm.png"
        while not self._element_exists(conv_confirm, 0.1) and \
                time.time()-start_time < 5:
            self._mabi_click(980, 530, delay=0.5)
            
    def _answer_conv_question(self):
        screen_text = self._get_screen_tesseract_text(775, 450, 820, 775)
        answer_key = {'mission': (820, 1180), 'train': (870, 1180), 
                      'play': (940, 1180), 'cook': (790, 1340), 
                      'dress': (840, 1340), 'embarrassed': (900, 1340)}
        print(screen_text)
        for answer in answer_key:
            if answer in screen_text:
                x, y = answer_key[answer]
                self._mabi_click(x, y, delay=0.5)
                break
                
    def _end_training(self):
        self._talk_to_squire()
        self._mabi_click(980, 670, delay=0.5)
        self._mabi_click(660, 1880, delay=0.5)
        self._mabi_click(610, 1000, delay=1)
        self._reset_char_screen()
        time.sleep(2)
    
    def _start_training(self, train_id):
        self._talk_to_squire()
        self._mabi_click(980, 670, delay=0.5)
        for i in range(train_id-6):
            self._mabi_click(600, 1900)
        loc = min(6, train_id)
        self._mabi_click(410+28*loc, 1600, delay=0.1)
        self._mabi_click(690, 1020, delay=0.5)
        self._reset_char_screen()
        time.sleep(2)
    
    def _end_conv(self):
        start_time = time.time()
        talk_confirm = "./confirms/talk_confirm.png"
        while self._element_exists(talk_confirm, 0.05) and \
                time.time()-start_time < 5:
            self._mabi_click(980, 530, delay=0.2)
        time.sleep(2)
    
    def _get_screen_tesseract_text(self, x1, y1, x2, y2):
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        text_cutout = screen[x1:x2, y1:y2]
        text_cutout = cv2.resize(text_cutout,None,fx=4,fy=4)
        ret, text_cutout = cv2.threshold(text_cutout,127,255,cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(text_cutout, config='--psm 12 --oem 3')
        return text
    
    def _reassign_missions(self, missions_by_id, squire_id, number=3):
        missions = missions_by_id[squire_id]
        self._complete_missions(number)
            
        self._mabi_click(420, 650, delay=0.1)
        self._mabi_click(450, 790, delay=0.5)
        self._assign_missions(missions)
        
    def _complete_missions(self, number):
        self._mabi_click(640, 290, delay=0.1)
        self._mabi_click(990, 330, delay=0.5)
        for i in range(number):
            self._select_mission(0)
            self._mabi_click(480, 520, delay=0.1)
            PressKey(W)
            ReleaseKey(W)
            self._mabi_click(600, 1000, delay=2)
            for j in range(4):
                self._mabi_click(590, 910+j*20)
              
    def _assign_missions(self, mission_chart):
        assigned_squires = 0
        for i in range(3):
            if mission_chart[i] < 0:
                continue
            self._select_mission(mission_chart[i])
            for j in range(3):
                if mission_chart[j] > mission_chart[i]:
                    mission_chart[j] -= 1
            self._select_squire(i - assigned_squires)
            self._mabi_click(480, 520, delay=0.1)
            self._mabi_click(610, 1020, delay=2)
            for j in range(4):
                self._mabi_click(590, 910+j*20)
            assigned_squires += 1
    
    def _reset_char_screen(self):
        for i in range(4):
            PressKey(ESC)
            ReleaseKey(ESC)
            time.sleep(0.2)
        PressKey(C)
        ReleaseKey(C)
        time.sleep(1)
        
    def _select_mission(self, i):
        if i > 5:
            self._mabi_click(755, 960, delay=0.1)
            i -= 6
        else:
            self._mabi_click(755, 930, delay=0.1)
        self._mabi_click(500+i*42, 780, delay=0.1)
        
    def _select_squire(self, i):
        self._mabi_click(180+i*80, 520, delay=0.1)
    
    def _login(self):
        self._mabi_click(1030, 50, delay=5)
        login_confirm = "./confirms/login_confirm.png"
        self._wait_for_element_or_timeout(login_confirm, 0.06, 15)
        time.sleep(2)
        
        new_day_confirm = "./confirms/new_day_confirm.png"
        if self._element_exists(new_day_confirm, 0.12):
            self._mabi_click(320, 1330, delay=1)
        
    def _logout(self):
        self._mabi_click(1060, 580, delay=0.5)
        self._mabi_click(980, 600, delay=0.5)
        self._mabi_click(600, 1000, delay=0.5)
        logout_confirm = "./confirms/logout_confirm.png"
        self._wait_for_element_or_timeout(logout_confirm, 0.06, 15)
        time.sleep(8)
    
    def _select_character(self, id):
        self._mabi_click(250+50*id, 1700, delay=1)
    
    def _wait_for_element_or_timeout(self, element_name, threshold, timeout):
        start_time = time.time()
        while (not self._element_exists(element_name, threshold)) and \
                time.time()-start_time < timeout:
            time.sleep(0.5)
    
    def _element_exists(self, img_name, threshold):
        screen = self.grab_screen()
        img = self.load_image(img_name)
        res = cv2.matchTemplate(screen, img, cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(res)
        #print(img_name, min_val, threshold, min_val < threshold)
        return min_val < threshold
        
    def grab_screen(self):
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        screen = cv2.resize(screen,None,fx=1/self.ir_factor,fy=1/self.ir_factor)
        return screen

    def load_image(self, img_name):
        img = cv2.imread(img_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.resize(img,None,fx=1/self.ir_factor,fy=1/self.ir_factor)
        return img
    
    def edge_difference(self, screen, img):
        screen = self._dist_transform(screen)
        img = self._dist_transform(img)
        res = cv2.matchTemplate(screen, img, cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(res)
        return min_val
    
    @staticmethod
    def _dist_transform(img):
        canny = cv2.Canny(img, 100, 200)
        dist = cv2.distanceTransform(canny,cv2.DIST_L1,5)
        return dist
    
    @staticmethod
    def _mabi_click(h, w, delay=None, clickDelay=0.1):
        pyautogui.moveTo(w, h)
        pyautogui.mouseDown(); 
        time.sleep(clickDelay); 
        pyautogui.mouseUp() 
        
        if delay:
            time.sleep(delay)
            
    @staticmethod
    def _mabi_zoom(cycle, amount, x=540, y=960):
        for i in range(cycle):
            pyautogui.moveTo(y, x)
            pyautogui.scroll(amount)
    
    @staticmethod
    def alt_tab():
        time.sleep(0.5)
        pyautogui.hotkey('alt', 'tab', interval=0.1)
        
    def box_buying(self, int_seals):
        self.alt_tab()
        for i in range(int_seals//30):
            self._mabi_click(90, 1645, delay=0.1)
            self._mabi_click(280, 1645, delay=0.9)
            self._mabi_click(395, 1795, delay=0.9)
        self.alt_tab()
        
    def make_leather_straps(self, num_leathers):
        self.alt_tab()
        for i in rawnge(num_leathers):
            pyautogui.keyDown("shiftleft")
            self._mabi_click(50, 400, delay=0.1)
            pyautogui.keyUp("shiftleft")
            self._mabi_click(130, 480, delay=0.1)
            self._mabi_click(380, 330, delay=1, clickDelay=0.5)
            self._mabi_click(490, 250, delay=5)
        self.alt_tab()
        
    def synthesize(self, num_syn):
        self.alt_tab()
        for i in range(num_syn):
            self._mabi_click(500, 1020, delay=1)
            self._add_item_to_craft(950, 160, 600, 190)
            self._add_item_to_craft(950, 185, 600, 250)
            self._add_item_to_craft(950, 210, 600, 310)
            self._mabi_click(700, 200, delay=5)
        self.alt_tab()
        
    def _add_item_to_craft(self, startx, starty, endx, endy):
        PressKey(SHIFT)
        self._mabi_click(startx, starty, delay=0.3)
        ReleaseKey(SHIFT)
        self._mabi_click(startx+80, starty+80, delay=0.8)
        self._mabi_click(endx, endy, delay=0.5)
    
    mission_charts = {0: [1, 3, 5], 1: [3, 2, 5], 2: [1, 3, 5], 3: [1, 3, 5],
                      4: [3, 2, 5], 5: [3, 2, 5], 6: [3, 2, 5], 7: [3, 2, 5],
                      8: [1, 3, 5], 9: [3, 2, 5], 10: [1, 3, 5], 11: [1, 3, 5]}
        
        
        
        
        