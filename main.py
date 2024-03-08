from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QGraphicsScene ,QLabel , QHBoxLayout
from PyQt5 import QtWidgets, uic, QtGui
from matplotlib.pyplot import figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtWidgets import QWidget
import matplotlib.pyplot as plt
from cmath import *
from numpy import *
import sys
from PyQt5.QtWidgets import QDialog
from scipy import signal
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pyqtgraph as pg
matplotlib.use('Qt5Agg')
from all_pass import MyDialog as all_pass

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=7, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(1, 1, 1)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi(r'task_6.ui', self)
        
        self.graph = pg.PlotItem()
        self.is_dragging = False
        

        self.canvas1 = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout1 = QtWidgets.QVBoxLayout()
        self.layout1.addWidget(self.canvas1)

        self.canvas_mag = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout_mag = QtWidgets.QVBoxLayout()
        self.layout_mag.addWidget(self.canvas_mag)

        self.canvas_phase = MplCanvas(self, width=5, height=4, dpi=100)
        self.layout_phase = QtWidgets.QVBoxLayout()
        self.layout_phase.addWidget(self.canvas_phase)


        # Track the selected marker for dragging
        self.selected_marker = None
        self.dragging_marker = None
        self.selected_primary_marker = None
        self.selected_conjugate_marker = None
        self.offset = (0, 0)
        
        # Connect mouse events
        
        self.canvas1.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas1.mpl_connect('button_release_event', self.on_release)


        self.last_cursor_pos = None
        self.mag_list = [0]
        self.time_list = [0]
        

        # Plot unit circle
        self.plot_unit_circle(self.canvas1, self.circle_graph,
                        self.layout1)
        
        
        self.pasez = all_pass(self)
        self.all_pass_filter_btn.clicked.connect(self.open_dialog)
        self.delete_zeros_btn.clicked.connect(self.delete_zeros)
        self.delete_poles_btn.clicked.connect(self.delete_poles)
        self.delete_all_btn.clicked.connect(self.delete_all)
        self.zero_radiobtn.toggled.connect(lambda: self.toggle_placement("zeros"))
        self.polae_radiobtn.toggled.connect(lambda: self.toggle_placement("poles"))

        self.hoverWidget.setMouseTracking(True)
        self.hoverWidget.mouseMoveEvent = self.calculateMousePosition



        # List to store added zeros and poles
        self.zeros = []
        self.poles = []

        self.zeros_list = []
        self.poles_list = []

        self.new_zeros = []
        self.new_poles = []
        self.filtered_signal = [0]
        self.lowpass = False



    def open_dialog(self):
        # Create and show the dialog
        dialog = all_pass(self)
        dialog.exec_()  

    
    def calculateMousePosition(self, event):
        cursor_pos = event.pos()
        # print(f"Mouse Position: ({cursor_pos.x()}, {cursor_pos.y()})")
        self.magnitude = (cursor_pos.x() + cursor_pos.y() ) /2
        self.drawGraph()


    def drawGraph(self):
        self.mag_list.append (self.magnitude)
        self.time_list.append(self.time_list[-1] + 0.0005)
        # print("Contents of self.mag_list:", self.mag_list)


        if self.time_list[-1] > 1.5:
            self.hoveredInput.plotItem.setXRange(
                self.time_list[-1] - 1.5,
                self.time_list[-1] + 1.5,
                padding=0
            )
            self.hoveredOutput.plotItem.setXRange(
                self.time_list[-1] - 1.5,
                self.time_list[-1] + 1.5,
                padding=0
            )

        self.hoveredInput.plotItem.clear()
        self.hoveredInput.plotItem.plot(
            x=self.time_list[-500:],
            y=self.mag_list[-500:],
            pen='b'  # Use 'b' for blue color
        )

        zeros_array = np.array(self.zeros_list).flatten()
        poles_array = np.array(self.poles_list).flatten()
        
        numerator, denominator = signal.zpk2tf(zeros_array, poles_array, 1)
        self.filtered_signal = signal.lfilter(numerator, denominator, self.mag_list.copy())


        self.hoveredOutput.plotItem.clear()
        self.hoveredOutput.plotItem.plot(
            x=self.time_list[-500:],
            y= np.real(self.filtered_signal[-500:]),
            pen='b'  # Use 'b' for blue color
        )


    def plot_unit_circle(self, canvas, widget, layout):
        # Plot unit circle using Matplotlib on the canvas
        angles = np.linspace(0, 2 * np.pi, 1000)
        x = np.cos(angles)
        y = np.sin(angles)
        canvas.axes.plot(x, y, 'k')  # Black color for the unit circle
        # Plot the x-axis (horizontal line)
        canvas.axes.axhline(0, color='k')  
        
        # Plot the y-axis (vertical line)
        canvas.axes.axvline(0, color='k')  
        
        # Set the limits to ensure the origin is at the center of the circle
        canvas.axes.set_xlim(-1.1, 1.1)
        canvas.axes.set_ylim(-1.1, 1.1)
        canvas.draw()
        widget.setCentralItem(self.graph)
        widget.setLayout(layout)



    def plot_frequency_response_mag(self, canvas_mag, widget, layout):
        # Create a system from zeros and poles
        zeros = [complex(x, y) for x, y in self.zeros_list]
        poles = [complex(x, y) for x, y in self.poles_list]

        w, h = signal.freqz_zpk(zeros, poles, 1.0)
        # Plot the magnitude response
        canvas_mag.axes.clear()
        canvas_mag.axes.semilogx(w, abs(h))
        canvas_mag.axes.set_xlabel('Frequency')
        canvas_mag.axes.set_ylabel('Magnitude (dB)')
        canvas_mag.axes.set_title('Magnitude Response')
        canvas_mag.axes.grid()
        canvas_mag.axes.set_xlim(0, 10)
        canvas_mag.draw()
        widget.setCentralItem(self.graph)
        widget.setLayout(layout)



    def plot_frequency_response_phase(self, canvas_phase, widget, layout, flag):
        # Create a system from zeros and poles
        zeros = [complex(x, y) for x, y in self.zeros_list]
        poles = [complex(x, y) for x, y in self.poles_list]
        # print("zeros complex : ", zeros)
        # print("poles complex : ", poles)

        if flag:
            # Extend zeros and poles lists with self.pasez.b and self.pasez.a  
            print("flag : ", flag)
            self.pasez.plot_final_phase_gain()
            zeros.extend(self.pasez.x_b_complex)
            poles.extend(self.pasez.y_a_complex)
            w, h = signal.freqz_zpk(zeros, poles, 1.0)
            phase = np.unwrap(np.angle(h))
            self.layout_phase.removeWidget(self.canvas_phase)
            self.canvas_phase = MplCanvas(self, width=5, height=4, dpi=100)
            # self.layout_phase = QtWidgets.QVBoxLayout()
            self.layout_phase.addWidget(self.canvas_phase)

            # Plot the phase response
            self.canvas_phase.axes.clear()
            self.canvas_phase.axes.semilogx(w, phase)
            self.canvas_phase.axes.set_xlabel('Frequency')
            self.canvas_phase.axes.set_ylabel('Phase (degrees)')
            self.canvas_phase.axes.set_title('Phase Response')
            self.canvas_phase.axes.grid()
            self.canvas_phase.axes.set_xlim(0, 10)
            self.canvas_phase.draw()
            widget.setCentralItem(self.graph)
            widget.setLayout(layout)

        else:
            # print("zeros : ", zeros)
            # print("poles : ", poles)

            # Compute the frequency response
            w, h = signal.freqz_zpk(zeros, poles, 1.0)

            # Plot the phase response
            canvas_phase.axes.clear()
            canvas_phase.axes.semilogx(w, np.angle(h, deg=True))
            canvas_phase.axes.set_xlabel('Frequency')
            canvas_phase.axes.set_ylabel('Phase (degrees)')
            canvas_phase.axes.set_title('Phase Response')
            canvas_phase.axes.grid()
            canvas_phase.axes.set_xlim(0, 10)
            canvas_phase.draw()
            widget.setCentralItem(self.graph)
            widget.setLayout(layout)


    def delete_zeros(self):
        # Delete all zeros on the plot      
        self.zeros = []
        self.zeros_list = []
        self.redraw_plot(delete_zeros=True)
        self.plot_frequency_response_mag(self.canvas_mag, self.frequancy_responce_graph, self.layout_mag)
        self.plot_frequency_response_phase(self.canvas_phase, self.phase_responce_graph, self.layout_phase, flag=False)


    def delete_poles(self):
        # Delete all poles on the plot  
        self.poles = []
        self.poles_list = []
        self.redraw_plot(delete_poles=True)
        self.plot_frequency_response_mag(self.canvas_mag, self.frequancy_responce_graph, self.layout_mag)
        self.plot_frequency_response_phase(self.canvas_phase, self.phase_responce_graph, self.layout_phase, flag=False)


    def delete_all(self):
        # Delete all poles and zeros on the plot
        self.zeros = []
        self.zeros_list = []
        self.poles = []
        self.poles_list = []
        self.redraw_plot()
        self.plot_frequency_response_mag(self.canvas_mag, self.frequancy_responce_graph, self.layout_mag)
        self.plot_frequency_response_phase(self.canvas_phase, self.phase_responce_graph, self.layout_phase, flag=False)



    def redraw_plot(self, delete_zeros=False, delete_poles=False):
        # Redraws the plot after removing zeros or poles
        self.canvas1.axes.clear()
        self.plot_unit_circle(self.canvas1, self.circle_graph, self.layout1)
        
        for zero in self.zeros:
            if not delete_zeros:
                # Unpack tuple if necessary and add the artist object
                if isinstance(zero, tuple):
                    self.canvas1.axes.add_artist(zero[0])  # Assuming the artist object is at index 0
                
        for pole in self.poles:
            if not delete_poles:
                # Unpack tuple if necessary and add the artist object
                if isinstance(pole, tuple):
                    self.canvas1.axes.add_artist(pole[0])  # Assuming the artist object is at index 0 
        self.canvas1.draw()


    def toggle_placement(self, mode):
        # Toggle between placing zeros or poles based on radio button selection
        self.mode = mode  # Set the mode to determine whether it's zeros or poles
        self.canvas1.mpl_connect('button_press_event', self.on_press)



    def on_press(self, event):
        if event.button == 1:  # Left mouse button
            if event.inaxes == self.canvas1.axes:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    # Check if any marker is clicked
                    for primary_marker, conjugate_marker in self.zeros + self.poles:
                        if primary_marker.contains(event)[0]:
                            self.selected_primary_marker = primary_marker
                            self.selected_conjugate_marker = conjugate_marker
                            self.offset = (primary_marker.get_offsets()[0][0] - x, primary_marker.get_offsets()[0][1] - y)
                            self.dragging_marker = True  # Set dragging mode
                            break
                    else:
                        # No primary marker clicked, add new marker
                        if self.mode == 'zeros':
                            if self.add_conjugates.isChecked():
                                if y != 0:
                                    # Add conjugate zero to the list
                                    conjugate_marker = self.canvas1.axes.scatter(x, -y, color='b', marker='o', s=100,
                                                                                facecolors='none', edgecolors='b',
                                                                                linewidths=2)
                                    primary_marker = self.canvas1.axes.scatter(x, y, color='b', marker='o', s=100,
                                                                            facecolors='none', edgecolors='b',
                                                                            linewidths=2)
                                    self.zeros.append((primary_marker, conjugate_marker))
                                    self.zeros_list.append((x, y))
                            else:
                                # Add zero to the list
                                marker = self.canvas1.axes.scatter(x, y, color='b', marker='o', s=100,
                                                                facecolors='none', edgecolors='b', linewidths=2)
                                self.zeros.append((marker, None))
                                self.zeros_list.append((x, y))
                        elif self.mode == 'poles':
                            if self.add_conjugates.isChecked():
                                if y != 0:
                                    # Add conjugate pole to the list
                                    conjugate_marker = self.canvas1.axes.scatter(x, -y, color='r', marker='x', s=100,
                                                                                linewidths=2)
                                    primary_marker = self.canvas1.axes.scatter(x, y, color='r', marker='x', s=100,
                                                                            linewidths=2)
                                    self.poles.append((primary_marker, conjugate_marker))
                                    self.poles_list.append((x, y))
                            else: 
                                # Add pole to the list
                                marker = self.canvas1.axes.scatter(x, y, color='r', marker='x', s=100, linewidths=2)
                                self.poles.append((marker, None))
                                self.poles_list.append((x, y))
                        self.canvas1.draw()
                
                print("position:", x,y)    
                if x<0:
                    self.lowpass = True    # print("poles list", self.poles_list)
        elif event.button == 3:  # Right mouse button for deletion
            self.delete_selected(event)
        self.plot_frequency_response_mag(self.canvas_mag, self.frequancy_responce_graph, self.layout_mag)
        self.plot_frequency_response_phase(self.canvas_phase, self.phase_responce_graph, self.layout_phase, flag=False)   


    def on_motion(self, event):
        if self.dragging_marker and self.selected_primary_marker is not None:
            if event.inaxes == self.canvas1.axes:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    # Update primary marker position while dragging
                    new_x_primary = x + self.offset[0]
                    new_y_primary = y + self.offset[1]
                    self.selected_primary_marker.set_offsets([(new_x_primary, new_y_primary)])

                    # Update conjugate marker position if it exists
                    if self.selected_conjugate_marker:
                        new_x_conjugate = new_x_primary
                        new_y_conjugate = -new_y_primary
                        self.selected_conjugate_marker.set_offsets([(new_x_conjugate, new_y_conjugate)])

                    # Update the zeros_list and poles_list outside the if condition
                    self.zeros_list = [tuple(primary.get_offsets()[0]) if primary is not None else None for primary, _
                                       in self.zeros]
                    self.poles_list = [tuple(primary.get_offsets()[0]) if primary is not None else None for primary, _
                                       in self.poles]

                    # Clear the axes before plotting
                    self.canvas_mag.axes.clear()
                    self.canvas_phase.axes.clear()

                    # Plot magnitude and phase responses
                    self.plot_frequency_response_mag(self.canvas_mag, self.frequancy_responce_graph, self.layout_mag)
                    self.plot_frequency_response_phase(self.canvas_phase, self.phase_responce_graph, self.layout_phase, flag = False)

                    # Redraw canvas
                    self.canvas1.draw()


    def on_release(self, event):
        if self.selected_primary_marker is not None:
            # Reset selected marker after release
            self.selected_primary_marker = None
            self.offset = (0, 0)
            self.dragging_marker = False
        self.plot_frequency_response_mag(self.canvas_mag, self.frequancy_responce_graph, self.layout_mag)
        self.plot_frequency_response_phase(self.canvas_phase, self.phase_responce_graph, self.layout_phase, flag = False)


    def delete_selected(self, event):
        x, y = event.xdata, event.ydata

        if x is not None and y is not None:
            clicked_position = np.array([x, y])
            min_distance = float('inf')
            closest_marker = None

            all_markers = self.zeros + self.poles  # Combine both zero and pole markers

            for primary_marker, conjugate_marker in all_markers:
                if primary_marker is not None:
                    marker_position = primary_marker.get_offsets()[0]
                    distance = np.linalg.norm(marker_position - clicked_position)
                    if distance < min_distance:
                        min_distance = distance
                        closest_marker = (primary_marker, conjugate_marker)

            if closest_marker is not None:
                if closest_marker in self.zeros:
                    self.zeros.remove(closest_marker)
                    self.zeros_list = [(primary_marker.get_offsets()[0][0], primary_marker.get_offsets()[0][1]) for primary_marker, _ in self.zeros]
                elif closest_marker in self.poles:
                    self.poles.remove(closest_marker)
                    self.poles_list = [(primary_marker.get_offsets()[0][0], primary_marker.get_offsets()[0][1]) for primary_marker, _ in self.poles]

                closest_marker[0].remove()  # Remove primary marker

                if closest_marker[1] is not None:
                    closest_marker[1].remove()  # Remove conjugate marker if it exists

        self.canvas1.draw()
        self.plot_frequency_response_mag(self.canvas_mag, self.frequancy_responce_graph, self.layout_mag)
        self.plot_frequency_response_phase(self.canvas_phase, self.phase_responce_graph, self.layout_phase, flag=False)




def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
