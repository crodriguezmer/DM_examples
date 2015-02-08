%% Preprocessing 

% This script performs preprocessing of anatomical and functional MRI data
% using SPM functions, but bypassing any interaction with the point and
% click tools. 

% A nice (toolbox independent) overview of what's being done here can be found at:
% https://ngp.usc.edu/files/2013/06/Lei_Preprocessing_08_11_2011.pdf

% Requires study folders organized in the following format
% STUDYNAME/STUDYNAMESUBJNO/run_000X  for functionals, where x = number of run.
% STUDYNAME/STUDYNAMESUBJNO/anat/  for anatomicals

% Processing performed:
% 1) Slice timming correction
% 2) Realignment of functionals to first image
% 3) Coregistration of T1 to realigned functional mean
% 4) Segmentation of corregistered T1
% 5) Normalization of functionals onto EPI template using segmentations
% 6) Smoothing of functionals

% This script can be adapted to any study with minor changes to the lines
% dealing with directories. The parameters are set favoring quality to
% speed of processing. Any subjects with poor registration into MNI space
% probably have an odd position in the scanner. The problem can be fixed by
% manually realigning the center of the first functional image, using the
% "Display" module in the GUI. The anterior commisure should be made as
% close to zero as possible.

% Parameter specification
clear all; clc;

% Add path
addpath('/../../spm8'); % point to spm directory. 
% warning: function have only been tested on spm8. other versions may need
% modifications. 

% primary directory
studydir = '/../../study'; % point to spm directory.  
% see above for required directory structure.
cd(studydir);

% get subject folders
subdirs = dir('STUDYNAME*'); % point to subject directories: 'STUDYNAMESUBJNO'

% protocol parameters
noRuns = X;  % how many different sessions (functinal runs)? 
nSlices = X; % specified in the scanning protocol
TR = X;      % specified in the scanning protocol

% Loop through subjects
for subj = 1:length(subdirs)
    
    
    % move to subject directory
    subjn = str2double(subdirs(subj).name);
    subjdir = sprintf('%s/%s', studydir,subdirs(subj).name);
    cd(subjdir);
    
    % get all relevant directories
    anatdir = sprintf('%s/anat',subjdir);
    funcdirs = dir('run_*');
    
    for i = 1:length(funcdirs)
        funcdirs(i).name = sprintf('%s/%s', subjdir, funcdirs(i).name);
    end

  %% 1) Slice Timming
  % correct for acquisition time.
  
    refslice = 1;
    sliceorder = [1:2:nSlices 2:2:nSlices]; % Interleaved ascending
    prefix = 'a';
    
    % Loop through runs and generate file names for this subject
    for f = 1:length(funcdirs)
        currdir = funcdirs{f};
        cd(currdir);  % cd to the appropriate run folder
        vols = dir('*.nii'); % point to functional volumes. can be 4d but best if a series of 3d vols.
        PP =[];
        for i = 1:length(vols)
            PP = [PP; fullfile(currdir, vols(i).name)];
        end
        
        P{f} = PP;
        
        % return to subject folder
        cd(subjdir);
        
    end
            
    TA = TR - TR/nSlices;
    
    timing(2) = TR - TA;
    timing(1) = TA / (nSlices -1);
    
    spm_slice_timing(P, sliceorder, refslice, timing, prefix);
    
    clear P
    clear vols
    
    %% 2) Realign to first image and then to mean
    % place all functional scans on the same space, 'eliminate' motion
    
    cd(subjdir);

    
    % % Set estimate options
    flags = struct('quality', .9, 'fwhm', 5, 'sep', 4, 'interp', 2,'wrap',[1 1 0]);
    
    P={}; % clear filenames array
    for f = 1:length(funcdirs)
        currdir = funcdirs{f};
        cd(currdir); % cd to the appropriate run folder
        vols = dir('a*.nii'); % point to time corrected vols. 
        % can point to resliced vols, if you want to evaluate performance
        % of motion correction function.
        PP =[];
        for i = 1:length(vols)
            PP = [PP; fullfile(currdir, vols(i).name)];
        end
        
        P{f} = PP;
        
        % cd back to subject folder
        cd(subjdir);
    end
    
    % Estimate
    spm_realign(P,flags);
    
    
    clear flags
    clear vols
    
    % Realignment write options
    flags = struct('interp', 4, 'which', 2, 'wrap', [1 1 0]', 'prefix', 'r');
    
    % Perform the realignment
    spm_reslice(P,flags);
    
    clear P
    clear flags
    
    % cd back to subject folder
    cd(subjdir);
    
    %% 3) Coregister T1 to meanravol 
    % place functional and anatomical scans on the same space
    
    % % Use mean as reference
    refDir = funcdirs{1};
    
    cd(refDir);
    refFolder = pwd;
    ref = dir('mean*');
    
    refFile = ref.name;
    VG = fullfile(refFolder, refFile);
    if ischar(VG), VG = spm_vol(VG); end;
    
    % % Use anatomy as source    
    cd(anatdir);
    source = dir('*.nii');
    
    sourceFile = source.name;
    VF = fullfile(anatdir, sourceFile);
    
    if ischar(VF) || iscellstr(VF), VF = spm_vol(strvcat(VF)); end;
   
    % % estimate coregistration
    flags = struct('sep',[4 2],'params',[0 0 0  0 0 0], 'cost_fun','nmi','fwhm',[7 7],...
        'tol',[0.01 0.01 0.01 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001],'graphics',0);
    spm_coreg(VG,VF,flags);
    
    clear flags
    
    P = char(VG.fname, VF.fname);
    
    % % Perform coregistration
    flags = struct('interp', 1, 'mask', 0,'mean', 0,'which', 1,'wrap',[0 0 0]',...
        'prefix','f'); % CHECK: which = 1, so that when image defining space is first in matrix, it is not resliced?
    spm_reslice(P, flags);
    
    clear P VF VG
     
    %% 4) Segment the corregistered anatomical
    % split white and grey matter and cerebrospinal fluid
    
    % % Get the T1 corregistered image
    cd(anatdir);
    seg = dir('f*');
    segFile = seg.name;
    VF = fullfile(anatdir, segFile);
    if ischar(VF) || iscellstr(VF), VF = spm_vol(strvcat(VF)); end;
    
    
    % Estimate segmentation
    % Set options
    flags_seg = struct('regtype', 'mni', 'warpreg', 1,...
        'warpco', 25, 'biasreg', 0.0001, 'biasfwhm', 50, 'samp', 2,...
        'ngaus', [2 2 2 4]);
    
    % % Segment
    results = spm_preproc(VF, flags_seg);
    
    % Reformat generated spatial normalization parameters
    [po,pin] = spm_prep2sn(results);
    
    % Save normalization parameters to file
    spm_prep2sn(results);
    
    
    % Write out segmented data
    % Set options
    flags_wrtseg = struct('GM', [0 0 1],'WM', [0 0 1], 'CSF', [0 0 1],...
        'biascor', 1, 'cleanup', 0);
    % Write
    spm_preproc_write(po, flags_wrtseg);
    
    %%  5) Normalize using the normalization parameters from segmentation
    % force brain into a standard space (MNI)
        
    % Normalize functional images
    cd(anatdir);
    
    % Specify normalization options
    flags = struct('interp',1,'vox', [2, 2, 2],...
        'bb',[-78 -112 -70; 78 76 85],'wrap',[0 0 0],'preserve',0,'prefix','w');
    
    % Load the parameters
    segParamsFile = dir('*_seg_sn.mat');
    prm = fullfile(anatdir, segParamsFile.name);
         
    % Loop through functional volumes
    for f = 1:length(funcdirs)
        currdir = funcdirs{f};
        cd(currdir); % cd to the appropriate run folder
        vols = dir('ra*.nii');
        fprintf('writing run %g ... \n', f);
        for i = 1:length(vols)
            Q = fullfile(currdir, vols(i).name);
            spm_write_sn(Q,prm,flags);
        end
        
        % cd back to subject folder
        cd(subjdir)
        
    end
    
    %% 6) Smooth
    % blur images, adds statistical power but sacrifices spatial
    % resolution. required for group analyses.
    
    kn = 8; % isometric kernel size, mm
    
    % load matrix of filenames
    for f = 1:length(funcdirs)
        currdir = funcdirs{f};
        cd(currdir); % cd to the appropriate folder
        vols = dir('w*.nii');
        fprintf('smoothing run %g ...\n', f);
        for i = 1:length(vols)
            P = fullfile(currdir, vols(i).name);
            prefixed = ['s' vols(i).name];
            Q = fullfile(currdir, prefixed);
            
            spm_smooth(P,Q,[kn kn kn]);
            
            clear P Q prefixed
        end
        
        % cd back to subj folder
        cd(subjdir)
    end
    
    clear vols
    
    % back to study directory
    cd ..
    
end