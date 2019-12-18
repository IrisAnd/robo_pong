function vid = init_vid(n)

% function initializing the camera

vid = videoinput('winvideo',n,'YUY2_640x480');
set(vid,'ReturnedColorSpace','rgb');
triggerconfig(vid,'manual')
set(vid,'TriggerRepeat',inf)
set(vid,'FramesPerTrigger',1)

% config = triggerinfo(vid);
% dev_info = imaqhwinfo('winvideo', 1);
% dev_info.SupportedFormats';
% vid_info = imaqhwinfo(vid);
src = getselectedsource(vid);
set(src,'ExposureMode','manual')
set(src,'Exposure',-5)
set(src,'Gain',48)
% src.FocusMode = 'manual';

end