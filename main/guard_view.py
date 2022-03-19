from __init__ import *


class Ui_GuardDialog(QDialog):
    def __init__(self):
        super(Ui_GuardDialog, self).__init__()
        loadUi(guard_ui, self)

        self.DetectFace.clicked.connect(self.show_detected_face_data)
        self.Clock.clicked.connect(self.clock_student)

        self.student_current_status = "unknown"
        self.name = "unknown"

        self.image = None

    @pyqtSlot()
    def startVideo(self, camera_name):
        """
        :param camera_name: link of camera or usb camera
        :return:
        """
        if len(camera_name) == 1:
            self.capture = cv2.VideoCapture(int(camera_name))
        else:
            self.capture = cv2.VideoCapture(camera_name)

        self.encode_list = np.load("img_metrix.npy")
        self.class_names = np.load("classes.npy")

        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def clock_student(self):

        now = datetime.datetime.now()

        if self.student_current_status != "Out...":

            self.CheckoutTime.setText(
                datetime.datetime.strftime(now, "%I:%M %p"))
            self.CheckoutDate.setText(
                datetime.datetime.strftime(now, "%d/%m/%Y"))

            self.student_current_status = "Out..."

        elif self.student_current_status == "Out...":

            self.CheckinTime.setText(
                datetime.datetime.strftime(now, "%I:%M %p"))
            self.CheckinDate.setText(
                datetime.datetime.strftime(now, "%d/%m/%Y"))

            self.student_current_status = "In Hostel"

    def show_detected_face_data(self):

        self.Name.setText(self.name)

        if self.name != "unknown":
            self.ProfileImage.setPixmap(
                QPixmap(f"TrainingData/{self.name}.jpg"))
            self.Status.setText('In Hostel')
        else:
            self.ProfileImage.setPixmap(
                QPixmap("resources/unknown.jpeg"))
            self.Status.setText('unknown')

        self.ProfileImage.setScaledContents(True)

    def face_rec_(self, frame, encode_list_known, class_names):

        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(
            frame, faces_cur_frame)
        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(
                encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(
                encode_list_known, encodeFace)
            self.name = "unknown"
            best_match_index = np.argmin(face_dis)
            # print("s",best_match_index)
            if match[best_match_index]:
                self.name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        return frame

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def update_frame(self):
        _, self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)
        self.displayImage(self.image, self.encode_list, self.class_names)

    def displayImage(self, image, encode_list, class_names):

        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)

        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(
            image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        self.LiveFeed.setPixmap(QPixmap.fromImage(outImage))
        self.LiveFeed.setScaledContents(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    new_window = Ui_GuardDialog()
    new_window.show()
    new_window.startVideo("1")
    sys.exit(app.exec_())