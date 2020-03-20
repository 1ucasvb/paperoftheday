# "PDF Paper of the Day" picker - by @LucasVB
# Scans for all PDF files in a given folder
#   and picks one at random for you to read.
# The probability a paper is picked gets smaller
#   as the number of pages increases.
# Requires PyPDF2, NumPy and SciPy

import glob
import random
import subprocess, os, platform
from PyPDF2 import PdfFileReader
import numpy as np
from scipy.stats import rv_discrete

# ------------------------- SETTINGS

# Location of the PDFs
PATH = "."

# Exponent determining how fast probabilities decay with number of pages
#   prob(npages) is proportional to (1/npages)^DECAYFACTOR
# Increase with your laziness
DECAYFACTOR = 1.0

# -------------------------

# Dictionary of PDFs grouped by page
papers = dict()

# Scan PDFs in the given folder, and grab their number of pages
for pdfpath in glob.glob(os.path.join(PATH, "*.pdf")):
	with open(pdfpath,'rb') as pdf:
		npages = PdfFileReader(pdf).getNumPages()
		if npages not in papers.keys():
			papers[npages] = []
		papers[npages].append(pdfpath)

# Assemble a discrete Zipf-like power law distribution for the number of pages
# A paper has a probability to be picked proportional to (1/npages)^DECAYFACTOR
# So if there are 5 papers with 2 pages, the probability of drawing a
#   2-page paper is proportional to 5/2, if DECAYFACTOR is 1.0
dist = np.array([[k,len(papers[k])/(k**DECAYFACTOR)] for k in sorted(papers.keys())])
# Properly normalize the distribution based on all papers
dist[:,1] /= np.sum(dist[:,1])

# Get a sample from this distribution. This is the number of pages in the picked paper.
npages = rv_discrete(values=dist.T).rvs()

# Pick one of the (npages)-page papers uniformly
paper = random.choice(papers[npages])

# Open the PDF with default application
#   (via https://stackoverflow.com/a/435669)
if platform.system() == 'Darwin': # macOS
	subprocess.call(('open', paper))
elif platform.system() == 'Windows': # Windows
	os.startfile(paper)
else: # Linux
	subprocess.call(('xdg-open', paper))

#EOF