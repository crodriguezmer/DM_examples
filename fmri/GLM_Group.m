%% Specify a group level GLM.
% This script does not estimate the model. It is assumed that you'll want
% to look at the result and will be finally interacting with the SPM GUI.
% To visualize the result, run this script, then launch spm ('spm fmri'),
% click on 'Results' and select the SPM file output by this script.

% This script will make a 'GroupResults' directory under the study
% directory, if one doesn't already exist, and place the group results
% there.

% For a nice overview of what this script does, see:
% http://www.fil.ion.ucl.ac.uk/spm/course/slides10-vancouver/02_General_Linear_Model.pdf

addpath(genpath('/../spm8'))
% some of the functions called below are deeper in the spm directory
% structure, thus genpath

% Clean up
clear; clc;

% Primary directory
studydir = '/../../..';
cd(studydir);

% Get subject folders
subdirs = dir('STUDYNAME*');

% Specify the constrast to be estimated at group level and the model from
% which it's coming.
contrasts = {'MyFirstContrast'};
firstLevelmodel = 'Mymodel';

for c = 1:length(contrasts)
    
    SecondLevelfolder = sprintf('%s/GroupResults/%s', studydir, contrasts{c});
    if exist(SecondLevelfolder,'dir')==0
        mkdir(SecondLevelfolder)
    end
    
    P = cell(length(subdirs),1);
    
    % Get contrst files
    for subj = 1:length(subdirs)
        
        % Specify subject
        subjNo = subdirs(subj).name;
        
        % SubjFolder
        subjFolder = sprintf('%s/%s', studydir, subjNo );
        cd(subjFolder);
        
        % modelFolder
        modelFolder = sprintf('%s/spm_%s', subjFolder, firstLevelmodel);
        
        % Get filenames
        P{subj} = sprintf('%s/spmT_000%d.img,1',modelFolder, c);
        
        % Go back to study directory
        cd(studydir)
    end
    
    cd(SecondLevelfolder)
    resultsdir = pwd;
    
    % Set-up the rest of the model
    job.des.t1.scans = P;
    job.dir = {resultsdir};
    job.cov = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
    job.masking.tm.tm_none = 1;
    job.masking.im = 1;
    job.masking.em = {''};
    job.globalc.g_omit = 1;
    job.globalm.gmsca.gmsca_no = 1;
    job.globalm.glonorm = 1;
    
    % Complete the design matrix
    SPM   = spm_run_factorial_design(job);
    
end

