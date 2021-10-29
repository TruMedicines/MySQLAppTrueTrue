import webapp.OCRReader as etch

# Class to store pill information
# Not currently used other than storing the pill image

class Pill():
    def __init__(self):
        self.progress = 100
        self.previous_progress = 150
        self.rect = None
        self.dark_cropped = None
        self.bright_cropped = None
        self.pill_face = None
        self.db_match = None
        self.best_distance = 99999
        self.etched_num = None
        self.complete = False

    def getProgress(self, res):
        if self.rect:
            self.previous_progress = self.progress
            self.progress = 100*((self.rect[1]+(self.rect[3]/2)) / res[1])
        return self.progress
        
    def continuation(self):
        movement = self.previous_progress - self.progress
        if movement >= 0 and movement < 8:
            #print("    pill cont good")
            return True
        else:
            #print("    pill cont bad")
            return False
    
    def initial_crop(self, dark, bright, res1, res2):
        x,y,w,h=self.rect
        b = 60
        w_rat = res2[0]/res1[0]
        h_rat = res2[1]/res1[1]

        px = int(x * w_rat)
        py = int(y * h_rat)
        pw = int(w * w_rat)
        ph = int(h * h_rat)
        
        self.dark_cropped = dark[py-b:py+ph+2*b, px-b:px+pw+2*b]
        self.bright_cropped = bright[py-b:py+ph+2*b, px-b:px+pw+2*b]
        
    def FindDatabaseMatch(self, nbrs, dic):
        improved = False
        match, dist = bf.get_database_match(self.pill_face, nbrs, dic, stepsize=1)
        if dist < self.best_distance:
            self.db_match = match
            self.best_distance = dist
            improved = True
        return improved, self.db_match, self.best_distance
        
    def readEtching(self):
        self.etched_num = etch.read_etched_pill(self.pill_face)
        return self.etched_num
        
            
