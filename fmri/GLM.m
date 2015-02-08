%% Estimate a general linear model on fMRI data. 
%For a nice overview of what this script does (and the other two that you 
% may need to run) see: 
% http://www.fil.ion.ucl.ac.uk/spm/course/slides10-vancouver/02_General_Linear_Model.pdf 

% The directory structure assumed here is the same as in the preprocessing
% script. Also, file names are assumed to correspond with the output of the
% preprocessing script convention. 

% Clean up
clear; clc;

% Primary directory
addpath('/../spm8'); % point to spm directory
studydir = '/../../..'; % point to study directory
cd(studydir);

% Get subject folders
subdirs = dir('STUDYNAME*');

% Loop through subjects
for subj = 1:length(subdirs)
    
    
    % Specify some parameters
    studyName = 'STUDYNAME';
    SPM.xY.RT  = X; % TR
    SPM.xBF.UNITS ='secs';
    SPM.xBF.name = 'hrf';
    SPM.xBF.Volterra = 1;
    save_SPM = 0;
    SPM.xGX.iGXcalc = 'Scaling';
    SPM.xX.K(:).HParam = 128;
    SPM.xVi.form = 'AR(1)';
    noRuns = X; % "Sessions"
    condNames = {'AnOnsetRegressor','AnotherOnsetRegressor'}; % Must have >=1
    paramNames = {'AmodulatorOfSomeOnsetRegressor'}; % optional
    modelName = 'Mymodel'; % all results will be stored in a folder with this name
    stabilizationscans = X; % specify a number of scans to ignore at the beggining of every run, to allow for signal stabilization
    tailscans = X; % add some scans after the last event. 
    
    %% Folders and behavioral files
    
    % Move to subject directory
    subjn = str2double(subdirs(subj).name);
    subjdir = sprintf('%s/%s', studydir,subdirs(subj).name);
    cd(subjdir);
    
    % Prints to track progress on screen
    fprintf(1, '\n\n\n Working on subject %d (%d of %d). \n', subjn, subj, length(subdirs));
    
    % Get relevant directories
    funcdirs = dir('run*');
    for i = 1:length(funcdirs)
        funcdirs(i).name = sprintf('%s/%s',subjdir,funcdirs(i).name);
    end
    
    % ModelFolder
    modelFolder = sprintf('%s/spm_%s', subjdir, modelName);
    
    if exist(modelFolder,'dir')==0
        mkdir(modelFolder)
    end
    
    % Load behavior file. this file should contain all the onset regressors
    % and, optionally, the modulators. the rest of the script assumes that 
    % this command loads a variable caled behavData.
    load('behaviordirectory/behaviorfileforsubject.mat');
    
    % make a table to specify the first and last scan to use on each run.
    vols2use = zeros(noRuns,2);
    for i=1:noRuns
        runData = behavData(behavData(:,X)==i, :); % X is the column number where the run is specified in the behavioral file
        sessVolnums  = ceil(runData(:,X)/SPM.xY.RT); % X is a column number where the last onsets in a trial (e.g. AnotherOnsetRegressor) are specified
        firstvol = stabilizationscans + 1; % scans to ignore
        lastVol  = sessVolnums(end) + tailscans; % add some volumes after last trial onset
        vols2use(i,:) = [firstvol lastVol]; 
    end
    
    %% Nuisance regressors (motion) and volume specification
    
    % Get filenames
    P = [];
    
    for run = 1:noRuns
        runDir = sprintf('%s', funcdirs(run).name);
        
        % Get motion regressor file names
        cd(runDir)
        motionFile = dir('rp_a*');
        sessVols  = dir('swra*.nii'); % these are the preprocessed volumes
        
        PP = [];
        for i = vols2use(run,1):vols2use(run,2)
            PP = strvcat(PP, fullfile(runDir, sessVols(i).name));
        end
        
        % Concatenate volume names
        P = strvcat(P,PP);
        
        % Motion regressors (usually required as nuissance regressors)
        C = dlmread(sprintf('%s/%s', runDir, motionFile.name));
        SPM.Sess(run).C.C = C(vols2use(run,1):vols2use(run,2),:); % Eliminate rows for cut scans
        SPM.Sess(run).C.name=  {'R1'  'R2'  'R3'  'R4'  'R5'  'R6'};
        SPM.nscan(run)= length(SPM.Sess(run).C.C);
        
    end
    
    % Place scan names in data field
    SPM.xY.P  = P;
    
    %% Analysis design
    
    for i = 1:noRuns
        
        % Select the session on the behavioral file
        sessBehData = behavData(behavData(:,X)==i,:); % same X as in line 73
        
        
        % Code FofferSV as a linear contrast
        AmodulatorOfSomeOnsetRegressor = sessBehData(:,Y); % some modulator specified on the behavioral file (e.g. response time)
        
        
        for c = 1:length(condNames)
            
            % Take onset modulator names from above
            U(c).name = condNames(c);  %- cell of names for each input or cause
            
            % Default to a delta function for HRF convolution (your choice)
            U(c).dur  = 0;  %- durations (in SPM.xBF.UNITS)
            
            
            if strcmpi(condNames(c), 'AnOnsetRegressor ')
                U(c).ons  = sessBehData(:,X) - stabilizationscans*SPM.xY.RT;  
                % X is column name with onsets, subtract the number of seconds occupied by scans to be ignored
                
                % make it a boxcar function instead of delta? (your choice)
                U(c).dur  = DurationofBoxCar;  %- durations (in SPM.xBF.UNITS)
                
                % Regressors (need to be specified even if no modulators are desired)
                U(c).P(1).name  = 'none'; %- parameter names*** use char()?
                U(c).P(1).P = []; %- parameter vector
                U(c).P(1).h  = 0;  %- order of polynomial expansion
                
                
            elseif strcmpi(condNames(c), 'AnotherOnsetRegressor')
                U(c).ons  = sessBehData(:, anotherX) - stabilizationscans*SPM.xY.RT;  
                % anotherX is column name with onsets, subtract the number
                % of seconds occupied by scans to be ignored.
                
                % Regressors (e.g. modulate AnotherOnsetRegressor by response time)
                U(c).P(1).name  = paramNames{1}; %- parameter names*** use char()?
                U(c).P(1).P = AmodulatorOfSomeOnsetRegressor; %- parameter vector
                U(c).P(1).h  = 1;  %- order of polynomial expansion
                
            end
            
        end
        
        % Attach model to run
        SPM.Sess(i).U = U;
        
    end
    
    % Process design
    cd(modelFolder);
    
    % Complete model specification
    SPM = spm_fMRI_design(SPM);
    SPM = spm_fmri_spm_ui(SPM);
    
    % Estimate model
    SPM = spm_spm(SPM);
    
    % Save SPM.mat
    cd(modelFolder)
    
    fprintf('%-40s: ','Saving SPM configuration')                           %-#
    if spm_matlab_version_chk('7') >= 0,
        save('SPM', 'SPM', '-V6');
    else
        save('SPM', 'SPM');
    end
    fprintf('%30s\n','...SPM.mat saved')                                    %-#
    
    % Clear for next subject
    clear P SPM
    
end
