import matplotlib.pyplot as plt

class Plot:

    def __init__(self):

        self.lines = []

    def add(self, dataset, relative=False, normalise=False):

        self.lines.append(dataset)

        for item in dataset:
            
            x_axis, y_axis = item.xy(relative)

            if normalise:

                div = abs(float(max([abs(a) for a in y_axis])))
                y_axis = [y / div for y in y_axis]
            
            plt.plot(x_axis, y_axis, label=str(item) )

        return

    def export(self):
        """ For each item in each dataset, export to .csv file """
        pass

    @staticmethod
    def display(legend=True):
        try:
            if legend: plt.legend()
            plt.show()
        except:
            pass
        return
        
