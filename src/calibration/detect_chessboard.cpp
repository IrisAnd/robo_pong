
#include "opencv.hpp"

using namespace std;
using namespace cv;

VideoCapture cap(0);
if (!cap.isOpened()) // if not success, exit program
{
    cout << "Cannot access camera" << endl;
}
namedWindow("cam", 1);
Mat frame;
bool check = cap.read(frame);
imshow("cam", frame);

Mat view = frame.clone();
Size boardsize = Size(4,7);
vector<Point2f> ptvec;

double square_length;



bool found = findChessboardCorners(frame, boardsize, ptvec, CALIB_CB_ADAPTIVE_THRESH);
drawChessboardCorners(view, boardsize, Mat(ptvec), found);
circle(view, ptvec[0],2,Scalar(255,0,0);
circle(view, ptvec.back(),2,Scalar(0,0,255);
imshow("corners",view);

double corner_dist;
corner_dist = sqrt(ptvec[0]^2+ptvec[1]^2);
pix_to_mm = square_length/corner_dist;
