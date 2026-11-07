"""Deterministic vector artwork separating the two scientific scenarios."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
out=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'Arial','pdf.fonttype':42,'svg.fonttype':'none'})
fig=plt.figure(figsize=(15,6),facecolor='white')
ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,150),ylim=(0,60));ax.axis('off')
navy='#16324F';teal='#007F82';red='#B44836';grey='#536477'
ax.text(5,55,'Committee selection: two separate audit scenarios',fontsize=25,weight='bold',color=navy)
for x,w,color in [(5,68,'#EDF6F6'),(78,67,'#F1F4FA')]:
 ax.add_patch(FancyBboxPatch((x,10),w,39,boxstyle='round,pad=0.5,rounding_size=1',facecolor=color,edgecolor='#D5E0EA'))
ax.text(8,44,'A  Equal initialization',fontsize=20,weight='bold',color=teal)
ax.text(39,37,'Reward the selected committee',ha='center',fontsize=17,color=navy)
ax.annotate('',xy=(39,29),xytext=(39,34),arrowprops=dict(arrowstyle='->',lw=2.5,color=teal))
ax.text(39,25,'No feasible next committee',ha='center',fontsize=19,weight='bold',color=red)
ax.text(39,17.3,'Under full membership exclusion\nand global reputation thresholds',ha='center',va='center',fontsize=16,color=navy,linespacing=1.4)
ax.text(81,44,'B  Separate audit scenario',fontsize=20,weight='bold',color=navy)
ax.text(111.5,37,'Two reputation levels; n = 16, k = 4\nFour high-score adversaries',ha='center',va='center',fontsize=16,color=grey,linespacing=1.35)
ax.text(111.5,29,'Uniform  →  Reputation-filtered',ha='center',fontsize=16,color=navy)
ax.text(82,23,'Bound exceedance',fontsize=15,color=grey)
ax.text(142,23,'0.245 → 0.336',ha='right',fontsize=19,weight='bold',color=red)
ax.text(82,16,'Jain index',fontsize=15,color=grey)
ax.text(142,16,'1.000 → 0.956',ha='right',fontsize=19,weight='bold',color=teal)
ax.text(75,5.9,'Conditional selection-model results, not verified FPoR implementation failures.',ha='center',fontsize=15,color=navy)
ax.text(75,2.3,'Byzantine-bound exceedance is a composition metric, not demonstrated attack success.',ha='center',fontsize=13,color=grey)
for ext in ['pdf','svg','png','tiff']:
 fig.savefig(out/f'graphical_abstract.{ext}',dpi=300,facecolor='white')
plt.close(fig)
print('Generated separate-scenario graphical abstract: 4500 x 1800 pixels, 300 dpi.')
