import subprocess
import re
import os

# def myrun(cmd):
#     """from http://blog.kagesenshi.org/2008/02/teeing-python-subprocesspopen-output.html
#     """
#     p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     stdout = []
#     while True:
#         line = p.stdout.readline()
#         stdout.append(line)
#         print line,
#         if line == '' and p.poll() != None:
#             break
#     return ''.join(stdout)


def demulti_bamfile(bamfile, barcode_list, outdir = "demulti_bam"):
    import subprocess
    import re
    import os
    p = subprocess.Popen(["samtools", "view", bamfile],
                         stdout = subprocess.PIPE,
                         stderr = subprocess.STDOUT)

    checked_reads = 1
    wellstat = {}
    wellstat["NNNNNNNNNNN"] = [0,0]
    while 1:
        line = p.stdout.readline()
        line = line.decode("UTF-8")
        if line == "" and p.poll() != None:
            break


        barcode = line[0:11]
        flag = line.split("\t")[1]

        #print(flag)

        # Now I have the barcode of the read from its name.
        # This information will now be used to determine
        # if a specific barcode was already seen before, and therefore
        # appended to an exisiting file, or if a new file should be created.

        regex_list = list()

        i = 0
        while i < len(barcode):
            reg = [x for x in barcode]
            reg[i] = "."
            reg = "".join(reg)
            regex_list.append(reg)
            i += 1

        regex = "|".join(regex_list)
        #print(regex)
        re_comp = re.compile(regex)

        matched = list(filter(re_comp.match, barcode_list))


        if len(matched) > 1:
            assoc_barcode = "NNNNNNNNNNN"
            if flag == "4":
                wellstat[assoc_barcode][1] += 1
            else:
                wellstat[assoc_barcode][0] += 1



        if len(matched) == 1:
            assoc_barcode = matched[0]
            if assoc_barcode in wellstat.keys():
                if flag == "4":
                    wellstat[assoc_barcode][1] += 1

                else:
                    wellstat[assoc_barcode][0] += 1

            else:
                wellstat[assoc_barcode] = [0, 0]
                if flag == "4":
                    wellstat[assoc_barcode][1] = 1
                else:
                    wellstat[assoc_barcode][0] = 1

        #print(assoc_barcode + " " + str(wellstat[assoc_barcode]) + " " + str(len(matched)))

        if checked_reads % 10000 == 0:
            print(checked_reads)

        checked_reads += 1

    return(wellstat)



if __name__ == "__main__":

    barcodes = []
    with open("AllBarcodes.txt", "r") as bc:
        for line in bc:
            barcodes.append(line.rstrip())

    wellstat = demulti_bamfile(bamfile = "testbamshort.bam", barcode_list = barcodes)


    with open("well_read_aligned_unaligned_counts.txt", "w") as outfile:
        for key, value in wellstat.items():
            counts = [str(x) for x in value]
            counts = ','.join(counts)
            outfile.write(key + "," + counts + "\n")

