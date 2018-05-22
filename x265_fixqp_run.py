
import os
import sys
sys.path.append("_CommonTools")
sys.path.append("_Process")
from input_yuv_config import *
from config import *
from TaskManager import *
from analyse_x265_log import *
from Tools import *
TM = TaskManager(worker_number)

x265_fullpath = bin_path + x265_exe
if not os.path.exists(x265_fullpath):
    print "Error, x265 exe not exist."
    exit(1)

final_result_file = out_path + "_x265_fixqp_result.log"
ClearFile(final_result_file)
AppendLine(final_result_file, "       target bitrate     bitrate(kbps)   Y      U      V       enc_fps") # title

# get total task number
total_task_num = 0
cur_task_num   = 0
for p in x265_presets:
    for yuv in test_yuvs:
        for qp in fix_quant_qps:
            total_task_num = total_task_num + 1

# ******** Fix Quant *******
for p in x265_presets:
    AppendLine(final_result_file, "\nPreset " + p)
    for yuv in test_yuvs:
        AppendLine(final_result_file, "    %s"%yuv)
        for qp in fix_quant_qps:
            width  = yuv_resolution[yuv][0]
            height = yuv_resolution[yuv][1]
            fps    = yuv_fps[yuv]
            out_log = "%sx265_%s_%s_qp%d.log"%(out_path, yuv, p, qp)
            bitstream =  "%sx265_%s_%s_qp%d.bin"%(out_path, yuv, p, qp)
            cmd    = x265_fullpath + \
                     " --preset %s"%p + \
                     " --tune psnr" + \
                     " --keyint %d"%key_int + \
                     " --bframes %d"%bframes + \
                     " --b-pyramid" + \
                     " --ref %d"%ref + \
                     " --qp %d"%qp + \
                     " --output %s"%bitstream + \
                     " --input-res %dx%d"%(width, height) + \
                     " --fps %d"%fps + \
                     " --frames %d"%enc_frames + \
                     " --log-level full" + \
                     " --psnr" + \
                     " --frame-threads 1" + \
                     " --no-wpp" + \
                     " --input %s"%yuv_fullpath[yuv]
            del_bitstream_cmd = "python _CommonTools\\rm_file.py %s"%bitstream

            cur_task_num = cur_task_num + 1
            print "process %4d / %4d"%(cur_task_num, total_task_num)

            if b_del_bitstream == True:
                cmdlist = (cmd, del_bitstream_cmd, )
            else:
                cmdlist = (cmd, )
            if b_cover_result or not is_log_intact(out_log):
                TM.newTaskList(cmdlist, (out_log, ))
        TM.clearAllTaskList() # wait until all task finished

        # collect result for this yuv
        for qp in fix_quant_qps:
            out_log = "%sx265_%s_%s_qp%d.log"%(out_path, yuv, p, qp)
            ana_result = x265_analyse(out_log)
            AppendLine(final_result_file, "        %7s           %9.2f     %5.2f  %5.2f  %5.2f     %6.2f"%(qp, ana_result[3], ana_result[0], ana_result[1], ana_result[2], ana_result[4]))