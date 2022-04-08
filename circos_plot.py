#! /usr/bin/env python3
'''
Create circos plot based on the variations found in a tped file using the lengths found in a TSV file
'''


import argparse
import random
import subprocess

def parse_args():
    parser= argparse.ArgumentParser(usage='circos_plot.py [vars] [var_colors] ...')
    parser.add_argument('vars', help='tped format file')
    parser.add_argument('var_colors', help='TSV file of colors and likelihoods for links')

    cust_args = parser.add_argument_group('customization')
    cust_args.add_argument('--your_color', default='184,109,41', help='RGB format for your chromosome color. Default = "184,109,41"')
    cust_args.add_argument('--ref_color', default='0,0,0', help='RGB format for reference chromosome color. Default = "0,0,0"')
    cust_args.add_argument('--rand_order', action='store_true', help='Randomize order of chromosomes in circle to add abstraction to graphic. Default=Off')
    return parser.parse_args()


# Track size of chromosomes here for accurate graphic
# Taken from: https://www.ncbi.nlm.nih.gov/assembly/GCF_000002285.5/#/st
dog_chrs = {122014068:'1', 69219345:'10', 72832428:'11', 72300020:'12',
            62895387:'13', 60430354:'14', 64389122:'15', 54556944:'16',
            63738581:'17', 54357284:'18', 52989165:'19', 82037489:'2',
            57984708:'20', 50232922:'21', 61822301:'22', 52413914:'23',
            46832179:'24', 51908704:'25', 38725074:'26', 46280981:'27',
            41264955:'28', 40893792:'29', 94329250:'3',  40067686:'30',
            39086971:'31', 41857359:'32', 31422675:'33', 51113282:'34',
            26040529:'35', 30723464:'36', 31754289:'37', 23973277:'38',
            87912527:'4', 88913986:'5', 80213190:'6', 80419774:'7',
            73585679:'8', 60315500:'9', 16727:'MT', 108808365:'X', 3937623:'Y'}


class Chromosome:
    '''
    Track the chromosomes and their characteristics
    '''
    num_to_class = {} # Chromosome number to class ID

    def __init__(self, chr_num, length):
        self.chr_num = chr_num
        self.length  = length
        self.var_color   = '' # To be assigned later

        # Update Chromosome dict with new chromosome
        Chromosome.num_to_class[chr_num] = self


def format_karyotype(rand_order):
    '''
    Generate karyotype format data from Chromosomes
    Randomize order of chromosome if prompted by user with rand_order
    '''

    chr_order = [] # Track personal chromosomes
    for c in Chromosome.num_to_class:
        length = Chromosome.num_to_class[c].length
        chr_order.append('chr - {0} {0} 0 {1} {0}\n'.format(c, length))
    if rand_order: # Shuffle chromosome order
        random.shuffle(chr_order)

    chr_order2 = [] # Track reference chromosomes
    for c in Chromosome.num_to_class:
        length = Chromosome.num_to_class[c].length
        chr_order2.append('chr - chr{0} chr{0} 0 {1} chr{0}\n'.format(c, length))
    if rand_order: # Shuffle chromosome order 
        random.shuffle(chr_order2)
    
    chr_order.extend(chr_order2) # Combine lists and send back
    return chr_order


#### Main Script ####
args = parse_args()

# Parse chromosome information into classes for future data
for length,c in dog_chrs.items():
    Chromosome(c, length)


# Write Circos Karyotype file
chr_order_karyo = format_karyotype(args.rand_order) # Prepare karyotype file format data 
with open('./circos_karyotype.txt', 'w') as k_file:
    # Write chromosomes to file
    for chromosome in chr_order_karyo:
        k_file.write(chromosome)

# Write Circos Links file
with open('./circos_links.txt', 'w') as l_file:
    # Assign colors to chromosomes based on color weights
    chromosomes = list(Chromosome.num_to_class.keys())
    chr_count_total = 0
    with open(args.var_colors, 'r') as c_file:
        next(c_file)
        for line in c_file:
            line = line.strip().split()
            chr_count = round(len(chromosomes) * float(line[1]))
            for chromosome in chromosomes[chr_count_total:chr_count_total+chr_count]:
                Chromosome.num_to_class[chromosome].var_color = line[0]
            chr_count_total += chr_count

    # Create links based on variations (Dog Embark Data)
    with open(args.vars, 'r') as infile:
        for line in infile:
            line = line.strip().split()

            if line[4] == line[5]: # Skip line if no variation 
                continue

            # Adjust chromosome name accordingly
            if line[0] == '0': # Skip unplaced scaffolds
                continue
            elif line[0] == '41' or line[0] == '39': # Force adjust chr41/chr39 to chrX
                line[0] = 'X'
            elif line[0] == '40': # Convert chr40 to chrY
                line[0] = 'Y'

            c = line[0]
            pos = line[3]
            color = Chromosome.num_to_class[c].var_color
            l_file.write('{0} {1} {1} chr{0} {1} {1} color={2}\n'.format(c, pos, color))

# Write Circos Config file
c_file_text = '' # Only do one write at the end for efficiency

c_file_text += 'karyotype = ./circos_karyotype.txt\n'

# Global color scheme
c_file_text += '# Global Color Scheme \n'
c_file_text += '<colors>\n'
for c in Chromosome.num_to_class.keys():
    c_file_text += '{0}*={1}\n'.format(c, args.your_color)
    c_file_text += 'chr{0}*={1}\n'.format(c, args.ref_color)
c_file_text += '</colors>\n'

# Basic required content
c_file_text += '<ideogram>\n\n<spacing>\n'
c_file_text += 'default = 0.005r # Spacing between out ring chunks\n'
c_file_text += '</spacing>\n\n'

# Ideogram layout details
c_file_text += '# Ideogram layout details\n'
c_file_text += 'radius           = 0.9r # Size of radius for outer ring\n'
c_file_text += 'thickness        = 80p # Thickness of outer ring\n'
c_file_text += 'fill             = yes # Fill chunks with color?\n'
c_file_text += 'stroke_color     = black # Color of chunk outline\n'
c_file_text += 'stroke_thickness = 0p # Thickness of outline\n'

# Ideogram label details
c_file_text += '#Ideogram label details\n'
c_file_text += 'show_label       = no # Show chunk labels?\n'
c_file_text += '</ideogram>\n'

# Tick details
# << SKIPPED FOR NOW >>

# Link Details
c_file_text += '# Links... The actual connections\n'
c_file_text += '<links>\n<link>\n'
c_file_text += 'file      = ./circos_links.txt\n'
c_file_text += 'radius    = 0.98r\n'
c_file_text += 'bezier_radius = 0.1r\n'
c_file_text += 'thickness = 1\n'
c_file_text += '</link>\n</links>\n\n'

# Default circos distributions to include
c_file_text += '# Default circos distributions to include\n'
c_file_text += '<image>\n<<include etc/image.conf>>\n</image>\n'
c_file_text += '<<include etc/colors_fonts_patterns.conf>>\n'
c_file_text += '<<include etc/housekeeping.conf>>\n'

with open('./circos.conf', 'w') as c_file:
    c_file.write(c_file_text) # Write everything to file
    
# Run circos with created files
subprocess.run('circos --conf ./circos.conf', shell=True)

