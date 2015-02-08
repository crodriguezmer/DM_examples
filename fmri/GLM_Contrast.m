%% Specify contrasts of some GLM 

%For a nice overview of what this script does, see: 
% http://www.fil.ion.ucl.ac.uk/spm/course/slides10-vancouver/02_General_Linear_Model.pdf 

% For SPM specific details see: spm_conman, spm_contrasts, spm_run_con

% Get clean subjects
clear; clc;

% specify the model to work on
modelName = 'Mymodel'; % all results will be stored in a folder with this name


% Primary directory
addpath('/../spm8'); % point to spm directory
studydir = '/../../..'; % point to study directory
cd(studydir);

% Get subject folders
subdirs = dir('STUDYNAME*');

% Loop through subjects
for subj = 1:length(subdirs)
    
    % Move to subject directory
    subjn = str2double(subdirs(subj).name);
    subjdir = sprintf('%s/%s', studydir,subdirs(subj).name);
    cd(subjdir);
    
    % print something to track progress on screen
    fprintf(1, '\n\n\n Working on subject %d (%d of %d). \n', subjn, subj, length(subdirs));
    
    % ModelFolder
    modelFolder = sprintf('%s/spm_%s', subjdir, modelName);
    cd(modelFolder);
    
    % Load 1st level model
    load('SPM.mat');
    

    % First contrast
    % the contrast matrix needs to match the design matrix (SPM.xX)
    % below it is assumed that there the model has three main regressors
    % (e.g. two onsets and one modulator), six motion regressors, four
    % runs, and thus four session constants to accomodate for the means of
    % each run. Here we look at the third regressor (e.g. AmodulatorOfSomeOnsetRegressor)
    value = [0;0;1; 0;0;0;0;0;0; ...
        0;0;1; 0;0;0;0;0;0; ...
        0;0;1; 0;0;0;0;0;0; ...
        0;0;1; 0;0;0;0;0;0; ...
        0;0;0;0];
    
    Fc = spm_FcUtil('Set','MyFirstContrast', 'T', 'c', value, SPM.xX.xKXs); %Fc = spm_FcUtil('Set',name, STAT, set_action, value, sX) <-- see spm_conman line 1273
    SPM.xCon=Fc;
    SPM = spm_contrasts(SPM,length(SPM.xCon)); %Fills in SPM.xCon and writes con_????.img, ess_????.img and SPM?_????.img
   

    
    % Second contrast
    % Here we look at the first regressor (AnOnsetRegressor)
    value = [1;0;0; 0;0;0;0;0;0; ...
        1;0;0; 0;0;0;0;0;0; ...
        1;0;0; 0;0;0;0;0;0; ...
        1;0;0; 0;0;0;0;0;0; ...
        0;0;0;0];
    
    Fc(2) = spm_FcUtil('Set','MySecondContrast', 'T', 'c', value, SPM.xX.xKXs); %Fc = spm_FcUtil('Set',name, STAT, set_action, value, sX) <-- see spm_conman line 1273
    SPM.xCon=Fc;
    SPM = spm_contrasts(SPM,length(SPM.xCon)); %Fills in SPM.xCon and writes con_????.img, ess_????.img and SPM?_????.img

    
    % Save SPM.mat
    cd(modelFolder)
    
    fprintf('%-40s: ','Saving SPM configuration')                           %-#
    if spm_matlab_version_chk('7') >= 0,
        save('SPM', 'SPM', '-V6');
    else
        save('SPM', 'SPM');
    end
    fprintf('%30s\n','...SPM.mat saved')                                    %-#
    
    clear SPM Fc
    cd .. % return to experiment folder
end
