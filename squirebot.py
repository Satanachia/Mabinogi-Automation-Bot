import copy
import cv2
import numpy as np
import pyautogui
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
import time

from directkeys import PressKey, ReleaseKey, W, A, S, D, SHIFT, CTRL, ESC, C, LEFT, RIGHT
from PIL import ImageGrab

class SquireBot:
    
    def __init__(self, dimx=1080, dimy=1920, apply_factor=False):
        self.ir_factor = 4
        self.x_sfactor = (dimx-1080)
        self.y_sfactor = (dimy-1920)
        self.x_cfactor = (dimx-1080)/2
        self.y_cfactor = (dimy-1920)/2
        self.apply_factor = apply_factor
        print("Initialized")
        
    def execute_repeated_action(self, start, num_chars, action, cycle=2260, **kwargs):
        while True:
            print("Starting", str(action))
            start_time = time.time()
            self.execute_action_on_squires(start, num_chars, action, **kwargs)
            
            i = 0
            while time.time() - start_time < cycle:
                if i % 5 == 0:
                    print(time.time()-start_time, cycle)
                i += 1
                time.sleep(60)
            start = 0
    
    def execute_action_on_squires(self, start, num_chars, action, **kwargs):
        self.alt_tab()
        
        for i in range(start):
            PressKey(RIGHT)
            ReleaseKey(RIGHT)
            time.sleep(0.1)
        
        for i in range(start, num_chars):
            kwargs['squire_id'] = i
            self._login(i)
            self._reset_char_screen()
            action(**kwargs)
            self._logout()
            
            PressKey(RIGHT)
            ReleaseKey(RIGHT)
            
        for i in range(num_chars):
            PressKey(LEFT)
            ReleaseKey(LEFT)
            time.sleep(0.1)
            
        self.alt_tab()
        print("Finished")
        
    def _counsel_squires(self, squire_id, **kwargs):
        self._complete_missions(3)
        self._reset_char_screen()
        self._enter_avalon_gate()
        self._mabi_zoom(12, -500)
        self._move_to_squire(("center", "kanna"), squire_id)
        self._end_training()
        self._counsel()
        self._move_to_squire(("kanna", "logan"), squire_id)
        self._end_training()
        self._counsel()
        self._move_to_squire(("logan", "dai"), squire_id)
        self._end_training()
        self._counsel()
    
    def _counsel(self):
        self._talk_to_squire(talk_delay=2)
        self._mabi_click(990, 750, delay=0.5, apply_sfactor=self.apply_factor)
        self._end_conv()
    
    def _train_advanced_squire(self, missions_by_id, squire_id, training_by_id, mission_number=3, **kwargs):
        self._reassign_missions(missions_by_id, squire_id, number=mission_number)
        self._reset_char_screen()
        self._enter_avalon_gate()
        self._mabi_zoom(12, -500)
        self._move_to_squire(("center", "kanna"), squire_id)
        self._end_training()
        #self._converse_with_squire()
        
        training = training_by_id[squire_id][0]
        self._start_training(training)
    
    def _enter_avalon_gate(self):
        self._mabi_click(640, 290, delay=0.1)
        self._mabi_click(950, 330, delay=0.5)
        avalon_confirm = "./confirms/avalon_confirm.png"
        self._wait_for_element_or_timeout(avalon_confirm, 0.07, 15)
        time.sleep(4)
        
    def _move_to_squire(self, iternary, squire_id):
        non_elf = squire_id in [0, 7, 8, 10]
            
        if iternary == ("center", "kanna"):
            duration = 5 if non_elf else 4
            PressKey(A)
            time.sleep(duration)
            ReleaseKey(A)
        
        if iternary == ("kanna", "logan"):
            duration = 11 if non_elf else 9
            PressKey(D)
            time.sleep(duration)
            ReleaseKey(D)
        
        if iternary == ("logan", "dai"):
            duration = 5 if non_elf else 4
            PressKey(D)
            time.sleep(duration)
            ReleaseKey(D)
    
    def _converse_with_squire(self):
        self._talk_to_squire(talk_delay=2)
        for i in range(3):
            self._click_through_text()
            time.sleep(1)
            self._answer_conv_question()
            time.sleep(1)
        self._end_conv()
    
    def _talk_to_squire(self, talk_delay=8):
        self._mabi_click(540, 960, delay=0.1, apply_cfactor=self.apply_factor)
        PressKey(CTRL)
        self._mabi_click(540, 960, delay=talk_delay, apply_cfactor=self.apply_factor)
        ReleaseKey(CTRL)
        
        screen_text = self._get_screen_tesseract_text(950, 450, 1000, 900, apply_factor=self.apply_factor)
        while 'Conversation' not in screen_text and 'Counsel' not in screen_text:
            self._mabi_click(980, 530, delay=0.5, apply_sfactor=self.apply_factor)
            screen_text = self._get_screen_tesseract_text(950, 450, 1000, 900, apply_factor=self.apply_factor)
        
    def _click_through_text(self):
        start_time = time.time()
        conv_confirm = "./confirms/conv_confirm.png"
        while not self._element_exists(conv_confirm, 0.08) and \
                time.time()-start_time < 20:
            self._mabi_click(980, 530, delay=0.5, apply_sfactor=self.apply_factor)
            
    def _answer_conv_question(self):
        for i in range(3):
            screen_text = self._get_screen_tesseract_text(775, 450, 820, 775, apply_factor=self.apply_factor)
            answer_key = {'mission': (820, 1180), 'train': (870, 1180), 
                          'play': (940, 1180), 'cook': (790, 1340), 
                          'dress': (840, 1340), 'embarrassed': (900, 1340)}
            #print(i, screen_text)
            for answer in answer_key:
                if answer in screen_text:
                    x, y = answer_key[answer]
                    self._mabi_click(x, y, delay=1, apply_sfactor=self.apply_factor)
                    break
                
    def _end_training(self):
        self._talk_to_squire()
        self._mabi_click(980, 670, delay=0.5, apply_sfactor=self.apply_factor)
        self._mabi_click(660, 1880, delay=0.5)
        self._mabi_click(610, 1000, delay=1, apply_cfactor=self.apply_factor)
        self._mabi_click(980, 530, delay=0.1, apply_sfactor=self.apply_factor)
        PressKey(W)
        ReleaseKey(W)
        self._reset_char_screen()
    
    def _start_training(self, train_id):
        self._talk_to_squire(talk_delay=3)
        self._mabi_click(980, 670, delay=0.5, apply_sfactor=self.apply_factor)
        for i in range(train_id-6):
            self._mabi_click(600, 1900)
        loc = min(6, train_id)
        self._mabi_click(410+28*loc, 1600, delay=0.1)
        self._mabi_click(690, 1020, delay=0.5, apply_cfactor=self.apply_factor)
        self._reset_char_screen()
        time.sleep(2)
    
    def _end_conv(self):
        start_time = time.time()
        talk_confirm = "./confirms/talk_confirm.png"
        while self._element_exists(talk_confirm, 0.05) and \
                time.time()-start_time < 15:
            self._mabi_click(980, 530, delay=1, apply_sfactor=self.apply_factor)
        time.sleep(2)
    
    def _get_screen_tesseract_text(self, x1, y1, x2, y2, apply_factor=False):
        screen = np.array(ImageGrab.grab())
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        y_factor = self.y_sfactor if apply_factor else 0
        x_factor = self.x_sfactor if apply_factor else 0
        
        text_cutout = screen[x1+x_factor:x2+x_factor, y1+y_factor:y2+y_factor]
        text_cutout = cv2.resize(text_cutout,None,fx=4,fy=4)
        ret, text_cutout = cv2.threshold(text_cutout,127,255,cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(text_cutout, config='--psm 12 --oem 3')
        #print(text)
        return text
    
    def _reassign_missions(self, missions_by_id, squire_id, number=3):
        missions = missions_by_id[squire_id]
        self._complete_missions(number)
        self._assign_missions(missions)
        
    def _complete_missions(self, number):
        self._mabi_click(640, 290, delay=0.1)
        self._mabi_click(990, 330, delay=0.5)
        for i in range(number):
            self._select_mission(0)
            self._mabi_click(480, 520, delay=0.1)
            PressKey(W)
            ReleaseKey(W)
            self._mabi_click(600, 1000, delay=2, apply_cfactor=self.apply_factor)
            for j in range(4):
                self._mabi_click(590, 910+j*20, apply_cfactor=self.apply_factor)
              
    def _assign_missions(self, mission_chart_master):
        self._mabi_click(420, 650, delay=0.1, apply_cfactor=self.apply_factor)
        self._mabi_click(450, 790, delay=0.5, apply_cfactor=self.apply_factor)
        
        mission_chart = copy.deepcopy(mission_chart_master)
        assigned_squires = 0
        for squire in mission_chart:
            if mission_chart[squire] < 0:
                continue
            self._select_mission(mission_chart[squire])
            for other_squires in mission_chart:
                if mission_chart[other_squires] > mission_chart[squire]:
                    mission_chart[other_squires] -= 1
                    
            self._select_squire(squire)
            self._mabi_click(480, 520, delay=0.1)
            self._mabi_click(610, 1020, delay=2, apply_cfactor=self.apply_factor)
            for j in range(4):
                self._mabi_click(590, 910+j*20, apply_cfactor=self.apply_factor)
            assigned_squires += 1
    
    def _reset_char_screen(self):
        for i in range(6):
            PressKey(ESC)
            ReleaseKey(ESC)
            time.sleep(0.2)
        PressKey(C)
        ReleaseKey(C)
        time.sleep(1)
        
    def _select_mission(self, i):
        if i > 5:
            self._mabi_click(748, 962, delay=0.1, apply_cfactor=self.apply_factor)
            i -= 6
        else:
            self._mabi_click(748, 938, delay=0.1, apply_cfactor=self.apply_factor)
        self._mabi_click(500+i*42, 780, delay=0.1, apply_cfactor=self.apply_factor)
        
    def _select_squire(self, squire):
        #self._mabi_click(180+i*80, 520, delay=0.1)
        screen = self.grab_screen()
        screen = screen[0:int(600/self.ir_factor), 0:int(900/self.ir_factor)]
        confirm = "./confirms/" + squire + "_confirm.png"
        img = self.load_image(confirm)
        res = cv2.matchTemplate(screen, img, cv2.TM_SQDIFF_NORMED)
        min_val, _, min_loc, _ = cv2.minMaxLoc(res)
        self._mabi_click(min_loc[1]*self.ir_factor+20, min_loc[0]*self.ir_factor+20, delay=0.1, apply_cfactor=self.apply_factor)
    
    def _login(self, squire_id):
        self._mabi_click(250+50*squire_id, 1700, multi_click=4)
        self._mabi_click(1030, 50, delay=5, apply_sfactor=self.apply_factor)
        login_confirm = "./confirms/login_confirm.png"
        self._wait_for_element_or_timeout(login_confirm, 0.08, 15)
        time.sleep(2)
        
        new_day_confirm = "./confirms/new_day_confirm.png"
        if self._element_exists(new_day_confirm, 0.12):
            self._mabi_click(320, 1330, delay=1, apply_cfactor=self.apply_factor)
        
    def _logout(self):
        self._mabi_click(1060, 580, delay=0.5, apply_sfactor=self.apply_factor)
        self._mabi_click(980, 600, delay=0.5, apply_sfactor=self.apply_factor)
        self._mabi_click(600, 1000, delay=0.5, apply_cfactor=self.apply_factor)
        logout_confirm = "./confirms/logout_confirm.png"
        self._wait_for_element_or_timeout(logout_confirm, 0.06, 15)
        time.sleep(8)
    
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
    
    def _mabi_click(self, h, w, delay=None, clickDelay=0.1, multi_click=1, apply_sfactor=False, apply_cfactor=False):
        #y_sfactor = self.y_sfactor if apply_sfactor else 1
        #x_sfactor = self.x_sfactor if apply_sfactor else 1
        y_sfactor = self.y_sfactor if apply_sfactor else 0
        x_sfactor = self.x_sfactor if apply_sfactor else 0
        y_cfactor = self.y_cfactor if apply_cfactor else 0
        x_cfactor = self.x_cfactor if apply_cfactor else 0
        
        for i in range(multi_click):
            pyautogui.moveTo(w+y_sfactor+y_cfactor, h+x_sfactor+x_cfactor)
            pyautogui.mouseDown(); 
            time.sleep(clickDelay); 
            pyautogui.mouseUp() 
        
        if delay:
            time.sleep(delay)
            
    @staticmethod
    def _mabi_zoom(cycle, amount, x=400, y=960):
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
        
        
        
        
        