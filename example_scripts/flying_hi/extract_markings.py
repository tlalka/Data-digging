import sys, os
import numpy as np
import pandas as pd
import json

#from get_workflow_info import get_workflow_info

project_name = "spiral-graph"

infile        = "%s-spiral-graph-classifications.csv" % project_name
#workflow_file = "%s-workflows.csv"       % project_name


workflow_id = 3590
workflow_version = 12.33

classifications_all = pd.read_csv(infile)

classifications_all['anno_json'] = [json.loads(q) for q in classifications_all['annotations']]

# only use classifications from the workflow & version we care about
in_workflow = classifications_all.workflow_version == workflow_version

classifications = classifications_all[in_workflow]

foth = open("%s-clean.csv"  % project_name, "w")


# write the header line for each of the files
# each has the basic classification information + the mark information
# including sanity check stuff + stuff we may never need, like the tool number
# and the frame the user drew the mark on, respectively

# the other/interesting marker is an ellipse+tag: {(x, y), (rx, ry), angle, text}
foth.write("mark_id,classification_id,subject_id,created_at,user_name,user_id,user_ip,tool,frame,x,y,rx,ry,angle,text\n")


# now extract the marks from each classification
# people who say Python should never need for loops are either way better at it
# than I am or have never dealt with Zooniverse classification exports
# (or both)
i_empty = 0
i_mark = 0
for i, row in enumerate(classifications.iterrows()):
    # row[0] is the index, [1] is the classification info
    cl = row[1]

    class_id   = cl['classification_id']
    subject_id = cl['subject_ids']
    created_at = cl['created_at']
    username   = cl['user_name']
    userid     = cl['user_id']
    userip     = cl['user_ip']

    # for anonymous users the userid field is blank so reads as NaN
    # which will throw an error later
    if np.isnan(userid):
        userid = -1

    # loop through annotations in this classification
    # (of which there can be arbitrarily many)
    for j, anno in enumerate(cl['anno_json']):
        # not sure we actually need these right now as there's only 1 task
        #thetask  = anno['task']
        #thelabel = anno['task_label']

        # first, if this classification is blank, just write the basic information
        if len(anno['value']) < 1:
            i_empty+=1
            femp.write("%d,%d,\"%s\",\"%s\",%d,%s\n" % (class_id, subject_id, created_at, username, userid, userip))
        else:
            # it's not empty, so let's collect other info
            # the marks themselves are in anno['value'], as a list
            for i_v, thevalue in enumerate(anno['value']):
                i_mark+=1

                # how we write to the file (and which file) depends on which tool
                # is being used
                #
                # the annotation json returns an integer that's the index of the
                # tools array we defined earlier
                # obviously I could just use the integer but this is easier to read
                # so worry about string vs int compare speeds when you have many
                # millions of classifications
             
                foth.write("%d,%d,%d,\"%s\",\"%s\",%d,%s,%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f,\"%s\"\n" % (i_mark, class_id, subject_id, created_at, username, userid, userip, thevalue['tool'], thevalue['frame'], thevalue['x'], thevalue['y'], thevalue['rx'], thevalue['ry'], thevalue['angle'], thevalue['details'][0]['value'].replace("\n","").encode('utf-8')))




foth.close()


print("Saved %d marks from %d classifications (of which %d were empty) to %s-marks-*.csv." % (i_mark, len(classifications), i_empty, project_name))


#
