#class will discribe all the results of the post processing
# for completness this class would be nice to contain box informations
# or even better enhenrices box 

"""class Results:
    def __init__(self):

        # also the results of the lin regression performed on the middle part of the hysteresis loop 
        # not thiks like total distance but only general orientation
        self.lin_Regression_res = None

        # f(x) = mx + c
        # m is the slope of the line
        self.m = None

        # b is ofsett of the line
        self.b = None

        # amount of simulated points in the margin
        self.number_points_in_margin = None

        # length of linear behaviour of the hysteresis loop
        # from 0 to point where sim values lear margin around the line
        self.x_max_lin = None
    

    def set_x_max_lin(self, x_max_lin):
        self.x_max_lin = x_max_lin

    def get_x_max_lin(self):
        return self.x_max_lin

    def set_number_points_in_margin(self, number_points_in_margin):
        self.number_points_in_margin = number_points_in_margin

    def get_number_points_in_margin(self):
        return self.number_points_in_margin
    
    def set_slope(self, slope):
        self.m = slope

    def get_slope(self):
        return self.m      
    
    def set_b(self, b):
        self.b = b

    def get_b(self):
        return self.b
 
    def set_res_of_optimization(self, res):
        self.lin_Regression_res = res

    def get_res_of_optimization(self):
        return self.lin_Regression_res
"""