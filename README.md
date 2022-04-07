# Genotype Viz

This program will generate a circos graph based on the variants reported by commercial genotyping companies like Embark, 23andMe, etc.

Currently, this script only supports Dog genotype data from Embark. Other formats can be supported on request.


## Prerequisites

- Python3
- [Circos](http://circos.ca/software/installation/)
	- NOTE: Circos installation requires Perl... and it all kind of sucks to install. Follow documentation and don't be afraid to google


## Usage
```
circos_plot.py [vars] [var_colors] ...

positional arguments:

  vars                  tped format file

  var_colors            TSV file of colors and likelihoods for links

optional arguments:
  -h, --help            show this help message and exit

customization:

  --your_color YOUR_COLOR

                        RGB format for your chromosome color. Default = "184,109,41"
  --ref_color REF_COLOR

                        RGB format for reference chromosome color. Default = "0,0,0"

  --rand_order          Randomize order of chromosomes in circle to add abstraction to graphic. Default=Off
```

This command will use the provided test files to generate a simple example file:

```
./circos_plot.py example/example.tped example/var_colors
```

## Parameter explanation

#### vars

Embark provides two raw data files. You will want to give this program the one that ends in `.tped`.

#### var_colors

See example/var_colors for formatting. First column is the RGB format color, second column is the percentage of lines that should be that color. Example colors are taken from Embark website results if you want to replicate that.

#### your_color

This will change the squares which represent YOUR dog.

#### ref_color

This will change the squares which represent the reference dog.

#### rand_order

This will shuffle the order of the reference and your dog chromosomes (but keep them separated from each other). This adds a bit of abstraction to the links and adds some "artistic" elements to the display.
