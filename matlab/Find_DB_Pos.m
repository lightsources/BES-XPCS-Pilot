

clear all;
close all;


fn_dir = './Results_UFXC/';
fn = 'Chip_R156_Silica_Burst_att0_Rq0_00001.mat';
x_guess = 2;
y_guess = 2;

full_hdf_filename = fullfile(fn_dir,fn);

a = load(full_hdf_filename);


X_E = 10.9;

Det_Dist = 3.9;
pix_size = 76e-6;

lambda = 12.398/X_E;
k0 = 2*pi/lambda;

pix2q = (pix_size/Det_Dist)*k0;
 

img_2D = a.viewresultinfo.result.aIt{1};

figure;imagesc(log(img_2D));axis image;axis xy;colorbar

pix_pos_x = meshgrid(1:size(img_2D,2),1:size(img_2D,1));
pix_pos_y = meshgrid(1:size(img_2D,1),1:size(img_2D,2))';





dim_x = 81;
dim_y = 91;
step_size = 0.1;

ROI_Dev=zeros(dim_x,dim_y);
x0=zeros(dim_x,1);
y0=zeros(dim_y,1);

for ii = 1:dim_x
    for jj = 1:dim_y
    
        x0(ii) = x_guess + (ii-floor(dim_x/2))*step_size;
        y0(jj) = y_guess + (jj-floor(dim_y/2))*step_size;
        
        % Calculate the distance from each pixel to the direct beam
        % position, and convert it into Q
        Q_map = sqrt((pix_pos_x-x0(ii)).^2 + (pix_pos_y-y0(jj)).^2)*pix2q;

        Int_ROI = img_2D(Q_map>0.0067 & Q_map<0.0069);
        ROI_Dev(ii,jj) = std(Int_ROI);
        
    end
end

%%
figure;imagesc(x0,y0,ROI_Dev');axis image;axis xy;title('ROI Int. Var.');
colorbar;
% caxis([0 2e-3]);



% figure;imagesc(pix_pos_x);axis image;axis xy;title('x');
% figure;imagesc(pix_pos_y);axis image;axis xy;title('y');

% figure;imagesc(Q_map);axis image;axis xy;title('Q');
% 
% check_ROI = zeros(size(img_2D,1),size(img_2D,2));
% check_ROI(Q_map>0.006 & Q_map<0.0062) = 10000;
% figure;imagesc(check_ROI);axis image;axis xy;title('Check ROI');



        