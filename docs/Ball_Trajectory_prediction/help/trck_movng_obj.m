clear all;close all ;clc;
vid = videoinput('winvideo',1,'YUY2_160X120');
set(vid,'TriggerRepeat',Inf);
vid.FrameGrabInterval = 2;
vid.returnedcolorspace='rgb';
vid_src = getselectedsource(vid);
set(vid_src,'Tag','tracking moving object');
start(vid)


while(vid.FramesAcquired<=200)
   data = getdata(vid,2); 
    A=data(:,:,:,1);B=data(:,:,:,2);
    a=im2double(A); b=im2double(B);
    %first frame croppping
    a1=a(1:size(a,1)/2,1:size(a,2)/2);
    a2=a(1:size(a,1)/2,((size(a,2)/2)+1):size(a,2));
    a3=a(((size(a,1))/2+1):size(a,1),1:size(a,2)/2);
    a4=a(((size(a,1)/2)+1):size(a,1),((size(a,2)/2)+1):size(a,2));
    C=a1;C(:,:,2)=a2;C(:,:,3)=a3;C(:,:,4)=a4;
    
   %second frames croppping
    b1=b(1:size(b,1)/2,1:size(b,2)/2);
    b2=b(1:size(b,1)/2,((size(b,2)/2)+1):size(b,2));
    b3=b(((size(b,1))/2+1):size(b,1),1:size(b,2)/2);
    b4=b(((size(b,1)/2)+1):size(b,1),((size(b,2)/2)+1):size(b,2));
    D=b1;D(:,:,2)=b2;D(:,:,3)=b3;D(:,:,4)=b4;
   nc1=normcor(a1,b1);
   nc2=normcor(a2,b2);
   nc3=normcor(a3,b3);
   nc4=normcor(a4,b4);
   nc=[nc1 nc2 nc3 nc4];
   avg_nc=(nc1+nc2+nc3+nc4)/4;    
   [min_nc ind_nc]=sort(nc,'ascend');
   if min_nc(1)<avg_nc

       diff_im=imabsdiff(C(:,:,ind_nc(1)),D(:,:,ind_nc(1)));
       diff_im=medfilt2(diff_im,[3 3]);
       diff_im=im2bw(diff_im,0.04);
       diff_im=bwareaopen(diff_im,100);
       bw=bwlabel(diff_im,8);
       stats=regionprops(bw,'BoundingBox','Centroid');
    
imshow(b)
    hold on
        for object=1:length(stats)
             bb=stats(object).BoundingBox;
            bc=stats(object).Centroid;
            rectangle('Position',bb,'EdgeColor','Y','LineWidth',2);
            plot(bc(1),bc(2),'-m+');
            a=text(bc(1)+15,bc(2), strcat('X:', num2str(round(bc(1))), 'Y:', num2str(round(bc(2)))));
            set(a, 'FontName', 'Arial', 'FontWeight', 'bold', 'FontSize', 12, 'Color', 'yellow');
        end
     
    hold off
    end
   
   if min_nc(2)<avg_nc

       diff_im=imabsdiff(C(:,:,ind_nc(2)),D(:,:,ind_nc(2)));
       diff_im=medfilt2(diff_im,[3 3]);
       diff_im=im2bw(diff_im,0.1);
       diff_im=bwareaopen(diff_im,50);
       bw=bwlabel(diff_im,8);
       stats=regionprops(bw,'BoundingBox','Centroid');
    
imshow(b)
    hold on
        for object=1:length(stats)
             bb=stats(object).BoundingBox;
            bc=stats(object).Centroid;
            rectangle('Position',bb,'EdgeColor','Y','LineWidth',2);
            plot(bc(1),bc(2),'-m+');
            a=text(bc(1)+15,bc(2), strcat('X:', num2str(round(bc(1))), 'Y:', num2str(round(bc(2)))));
            set(a, 'FontName', 'Arial', 'FontWeight', 'bold', 'FontSize', 12, 'Color', 'yellow');
        end
     
    hold off
    end
   
   if min_nc(3)<avg_nc

       diff_im=imabsdiff(C(:,:,ind_nc(3)),D(:,:,ind_nc(3)));
       diff_im=medfilt2(diff_im,[3 3]);
       diff_im=im2bw(diff_im,0.1);
       diff_im=bwareaopen(diff_im,50);
       bw=bwlabel(diff_im,8);
       stats=regionprops(bw,'BoundingBox','Centroid');
    
imshow(b)
    hold on
        for object=1:length(stats)
             bb=stats(object).BoundingBox;
            bc=stats(object).Centroid;
            rectangle('Position',bb,'EdgeColor','Y','LineWidth',2);
            plot(bc(1),bc(2),'-m+');
            a=text(bc(1)+15,bc(2), strcat('X:', num2str(round(bc(1))), 'Y:', num2str(round(bc(2)))));
            set(a, 'FontName', 'Arial', 'FontWeight', 'bold', 'FontSize', 12, 'Color', 'yellow');
        end
     
    hold off
   end
    
   if min_nc(4)<avg_nc

       diff_im=imabsdiff(C(:,:,ind_nc(4)),D(:,:,ind_nc(4)));
       diff_im=medfilt2(diff_im,[3 3]);
       diff_im=im2bw(diff_im,0.1);
       diff_im=bwareaopen(diff_im,50);
       bw=bwlabel(diff_im,8);
       stats=regionprops(bw,'BoundingBox','Centroid');
    
imshow(b)
    hold on
        for object=1:length(stats)
             bb=stats(object).BoundingBox;
            bc=stats(object).Centroid;
            rectangle('Position',bb,'EdgeColor','Y','LineWidth',2);
            plot(bc(1),bc(2),'-m+');
            a=text(bc(1)+15,bc(2), strcat('X:', num2str(round(bc(1))), 'Y:', num2str(round(bc(2)))));
            set(a, 'FontName', 'Arial', 'FontWeight', 'bold', 'FontSize', 12, 'Color', 'yellow');
        end
     
    hold off
    end
end
stop(vid)
