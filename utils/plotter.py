import matplotlib.pyplot as plt
from cycler import cycler
import seaborn as sns
import numpy as np
import os
import math
from fears.utils import dir_manager, results_manager
import networkx as nx

def plot_timecourse(pop,counts_t=None,title_t=None):
    
    if (pop.counts == 0).all() and counts_t is None:
        print('No data to plot!')
        return
    elif counts_t is None:
        counts = pop.counts
    else:
        counts = counts_t # an input other than pop overrides pop
    if title_t is not None:
        title = title_t
    else:
        title = pop.fig_title    
        
    left = 0.1
    width = 0.8
    
    if pop.plot_entropy == True:
        fig,(ax1,ax3) = plt.subplots(2,1,figsize=(6,4),sharex=True) 
        ax3.set_position([left, 0.2, width, 0.2]) # ax3 is entropy
    else:
        fig,ax1 = plt.subplots(1,1,figsize=(6,4),sharex=True)
    
    ax1.set_position([left, 0.5, width, 0.6]) # ax1 is the timecourse
            
    counts_total = np.sum(counts,axis=0)
    
    sorted_index = counts_total.argsort()
    sorted_index_big = sorted_index[-8:]
    
    colors = sns.color_palette('bright')
    colors = np.concatenate((colors[0:9],colors[0:7]),axis=0)
    
    # shuffle colors
    colors[[14,15]] = colors[[15,14]]
    
    cc = (cycler(color=colors) + 
          cycler(linestyle=['-', '-','-','-','-','-','-','-','-',
                            '--','--','--','--','--','--','--']))
    
    ax1.set_prop_cycle(cc)

    color = [0.5,0.5,0.5]
    
    if pop.fitness_data == 'generate':
        ax2 = ax1.twinx() # ax2 is the drug timecourse
        ax2.set_position([left, 0.5, width, 0.6])
        ax2.set_ylabel('Drug Concentration (uM)', color=color,fontsize=20) # we already handled the x-label with ax1
        
        # if pop.drug_log_scale:
        #     if all(pop.drug_curve>0):
        #         drug_curve = np.log10(pop.drug_curve)
        #     yticks = np.log10([10**-4,10**-3,10**-2,10**-1,10**0,10**1,10**2,10**3])    
        #     ax2.set_yticks(yticks)
        #     ax2.set_yticklabels(['0','$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^{0}$',
        #                      '$10^1$','$10^2$','$10^3$'])
        #     ax2.set_ylim(-4,3)
        # else:
        drug_curve = pop.drug_curve
        ax2.plot(drug_curve, color='black', linewidth=2.0)
        ax2.tick_params(axis='y', labelcolor=color)
        
        if pop.drug_log_scale:
            ax2.set_yscale('log')
            if min(drug_curve) <= 0:
                axmin = 10**-3
            else:
                axmin = min(drug_curve)
            ax2.set_ylim(axmin,2*max(drug_curve))
            ax2.legend(['Drug Conc.'],loc=(1.3,0.93),frameon=False,fontsize=15)
            
        else:
            ax2.set_ylim(0,1.1*max(drug_curve))
            ax2.legend(['Drug Conc.'],loc=(1.25,0.93),frameon=False,fontsize=15)

            
        ax2.tick_params(labelsize=15)
        ax2.set_title(title,fontsize=20)
        
    
    # if pop.normalize:
    #     counts = counts/np.max(counts)
        
    for allele in range(counts.shape[1]):
        if allele in sorted_index_big:
            ax1.plot(counts[:,allele],linewidth=3.0,label=str(helpers.int_to_binary(allele)))
        else:
            ax1.plot(counts[:,allele],linewidth=3.0,label=None)
            
    ax1.legend(loc=(1.25,-.12),frameon=False,fontsize=15)
        
    ax1.set_xlim(0,pop.x_lim)
    ax1.set_facecolor(color='w')
    ax1.grid(False)

    ax1.set_ylabel('Cells',fontsize=20)
    ax1.tick_params(labelsize=15)
    
    if pop.plot_entropy == True:
        e = pop.entropy(counts)
        
        ax3.plot(e,color='black')
        ax3.set_xlabel('Time',fontsize=20)
        ax3.set_ylabel('Entropy',fontsize=20)
        if pop.entropy_lim is not None:
            ax3.set_ylim(0,pop.entropy_lim)
        ax3.tick_params(labelsize=15)
    
    if pop.y_lim is not None:
        y_lim = pop.y_lim
    else:
        y_lim = np.max(counts) + 0.05*np.max(counts)
    
    if pop.counts_log_scale:
        ax1.set_yscale('log')
        # ax1.set_ylim(1,5*10**5)
    else:
        ax1.set_ylim(0,y_lim)
    
    xlabels = ax1.get_xticks()
    xlabels = xlabels*pop.timestep_scale
    xlabels = xlabels/24
    xlabels = np.array(xlabels).astype('int')
    ax1.set_xticklabels(xlabels)
    ax1.set_xlabel('Days',fontsize=20)

    plt.show()
    return fig

def plot_fitness_curves(pop,
                        fig_title='',
                        plot_r0 = False,
                        save=False,
                        savename=None,
                        ax=None,
                        labelsize=20,
                        linewidth=3):
    
    # drugless_rates = pop.drugless_rates
    # ic50 = pop.ic50
    
    if ax is None:
        fig, ax = plt.subplots(figsize = (10,6))
        show_legend=True
    else:
        show_legend = False
    
    powers = np.linspace(-3,5,20)
    conc = np.power(10*np.ones(powers.shape[0]),powers)
    
    
    colors = sns.color_palette('bright')
    colors = np.concatenate((colors[0:9],colors[0:7]),axis=0)
    colors[[14,15]] = colors[[15,14]]
    
    cc = (cycler(color=colors) + 
           cycler(linestyle=['-', '-','-','-','-','-','-','-','-',
                            '--','--','--','--','--','--','--']))
    ax.set_prop_cycle(cc) 
    
    fit = np.zeros((pop.n_genotype,conc.shape[0]))
    
    for j in range(conc.shape[0]):
        fit[:,j] = pop.gen_fit_land(conc[j])
    
    if plot_r0:
        fit = fit-pop.death_rate
        ylabel = '$R_{0}$'
        thresh = np.ones(powers.shape)
        ax.plot(powers,thresh,linestyle='dashdot',color='black',linewidth=linewidth)
    else:
        ylabel = 'Growth Rate'
    
    for gen in range(pop.n_genotype):
        ax.plot(powers,fit[gen,:],linewidth=linewidth,label=str(helpers.int_to_binary(gen)))
        
    # for allele in range(16):
        
    #     if pop.static_topology:
    #         for j in range(conc.shape[0]):
    #                fit[j] = pop.gen_fitness(allele,conc[j],drugless_rates,ic50)            
    #     else:
    #         for j in range(conc.shape[0]):
    #             fit[j] = pop.gen_fitness(allele,conc[j],drugless_rates,ic50)
            
    #     if plot_r0:
    #         fit = fit - pop.death_rate
    #         ylabel = '$R_{0}$'
    #         thresh = np.ones(powers.shape)
    #         ax.plot(powers,thresh,linestyle='dashdot',color='black',linewidth=3)
    #     else:
    #         ylabel = 'Growth Rate'
            
    #     ax.plot(powers,fit,linewidth=3,label=str(pop.int_to_binary(allele)))
    
    if show_legend:
        ax.legend(fontsize=labelsize,frameon=False,loc=(1,-.10))
    ax.set_xticks([-3,-2,-1,0,1,2,3,4,5])
    ax.set_xticklabels(['$10^{-3}$','$10^{-2}$','$10^{-1}$','$10^{0}$',
                         '$10^1$','$10^2$','$10^3$','$10^4$','$10^5$'])
    
    plt.title(fig_title,fontsize=labelsize)
    plt.xticks(fontsize=labelsize)
    plt.yticks(fontsize=labelsize)
    
    plt.xlabel('Drug concentration ($\mathrm{\mu}$M)',fontsize=labelsize)
    plt.ylabel(ylabel,fontsize=labelsize)
    ax.set_frame_on(False)
    
    if save:
        if savename is None:
            savename = 'fitness_seascape.pdf'
        r = dir_manager.get_project_root()
        savename = str(r) + os.sep + 'figures' + os.sep + savename
        plt.savefig(savename,bbox_inches="tight")
    
    return ax

def plot_msw(pop,fitness_curves,conc,genotypes,save=False):
    """
    plot_msw: method for plotting mutant selection window figures.

    Parameters
    ----------
    pop : population_class object
        
    fitness_curves : numpy array
        Columns 1-N represents a genotype that is a neighbor of column 0 
        (ancestor). Rows represent drug concentration.
    conc : numpy array
        Drug concentration used to calculate fitness_curves
    genotypes : list of ints
        Genotypes that were used to calculate the fitness_curves.
    save : bool
    
    Returns
    -------
    fig : figure object
        MSW figures

    """
    n_genotype = fitness_curves.shape[1]
    rows = int((n_genotype-1)/2)
    fig, ax = plt.subplots(rows,2)
    g = 1
    wt_fitness_curve = fitness_curves[:,0]
    for r in range(rows):
        for col in range(2):
           
            ax[r,col].plot(conc,wt_fitness_curve,label='wt',linewidth=3)
            
            cur_fitness_curve = fitness_curves[:,g]
            gt = genotypes[g]
            bitstring = pop.int_to_binary(gt)    
            ax[r,col].plot(conc,cur_fitness_curve,label=bitstring,linewidth=3)
            
            msw_left_assigned = False
            msw_right_assigned = False
            if wt_fitness_curve[0] > cur_fitness_curve[0] \
                and any(cur_fitness_curve>wt_fitness_curve):
                for c in range(len(conc)):
                    if wt_fitness_curve[c] < cur_fitness_curve[c] \
                        and msw_left_assigned is False:
                        msw_left = conc[c]
                        msw_left_assigned = True
                    if (cur_fitness_curve[c] < 1 
                        and msw_right_assigned is False):
                        msw_right = conc[c]
                        msw_right_assigned = True
                if msw_left < msw_right:
                    ax[r,col].axvspan(msw_left, msw_right, 
                                      facecolor='#2ca02c',alpha=0.5,
                                      label='MSW')
            
            ax[r,col].set_xscale('log')
            ax[r,col].legend(fontsize=10,frameon=False)

            g+=1
            
    for r in range(rows):
        ax[r,0].set_ylabel('$R_{0}$',fontsize=10)
    for c in range(2):
        ax[rows-1,c].set_xlabel('Drug concentration ($\mathrm{\mu}$M)',
                              fontsize=10)
    if save:
        r = dir_manager.get_project_root()
        savename = str(r) + os.sep + 'figures' + os.sep + 'msw.pdf'
        plt.savefig(savename,bbox_inches="tight")
    
    return fig

def gen_timecourse_axes(pop,
                        counts,
                        counts_ax,drug_curve=None,
                        drug_ax=None,
                        labelsize=15,
                        linewidth=3):
    
    # if pop is not None:
    #     drug_log_scale = pop.drug_log_scale
    #     x_lim = pop.x_lim
    # else:
    #     drug_log_scale = False
    #     x_lim = counts.shape[0]
    
    counts_total = np.sum(counts,axis=0)
    sorted_index = counts_total.argsort()
    sorted_index_big = sorted_index[-8:]    
    colors = sns.color_palette('bright')
    colors = np.concatenate((colors[0:9],colors[0:7]),axis=0)
    colors[[14,15]] = colors[[15,14]]
    
    cc = (cycler(color=colors) + 
          cycler(linestyle=['-', '-','-','-','-','-','-','-','-',
                            '--','--','--','--','--','--','--']))
    
    counts_ax.set_prop_cycle(cc)
    
    # color = [0.5,0.5,0.5]
    
    if drug_curve is not None:
        if drug_ax is None:
            raise Exception('No drug axes given')
        drug_ax.plot(drug_curve,color='black',linewidth=2)
        if pop.drug_log_scale:
            drug_ax.set_yscale('log')
            if min(drug_curve) <= 0:
                axmin = 10**-3
            else:
                axmin = min(drug_curve)
            drug_ax.set_ylim(axmin,2*max(drug_curve))
        else:
            drug_ax.set_ylim(0,1.1*max(drug_curve))
        drug_ax.tick_params(labelsize=labelsize)
    
    for genotype in range(counts.shape[1]):
        if genotype in sorted_index_big:
            counts_ax.plot(counts[:,genotype],linewidth=linewidth,
                           label=str(pop.int_to_binary(genotype)))
        else:
            counts_ax.plot(counts[:,genotype],linewidth=linewidth,label=None)
    
    if pop.counts_log_scale:
        counts_ax.set_yscale('log')
        yl = counts_ax.get_ylim()
        yl = [10**1,yl[1]]
        counts_ax.set_ylim(yl)
    
    counts_ax.set_xlim(0,pop.x_lim)
    counts_ax.set_facecolor(color='w')
    counts_ax.grid(False)
    # counts_ax.set_ylabel('Cells',fontsize=20)
    counts_ax.tick_params(labelsize=labelsize)

    xlabels = counts_ax.get_xticks()
    xlabels = xlabels*pop.timestep_scale
    # print(str(pop.timestep_scale))
    xlabels = xlabels/24
    xlabels = np.array(xlabels).astype('int')
    counts_ax.set_xticklabels(xlabels)

    return counts_ax, drug_ax


def plot_landscape(p,conc=10**0,fitness=None,relative=True):
    """
    Plots a graph representation of this landscape on the current matplotlib figure.
    If p is set to a vector of occupation probabilities, the edges in the graph will
    have thickness proportional to the transition probability between nodes.
    """
    if fitness is None:
        fitness = p.gen_fit_land(conc)
    
    if relative:
        fitness = fitness-min(fitness)
        fitness = fitness/max(fitness)
    
    # Figure out the length of the bit sequences we're working with
    N = int(np.log2(len(fitness)))

    # Generate all possible N-bit sequences
    n_genotype = len(fitness)
    genotypes = np.arange(2**N)
    genotypes = [p.int_to_binary(g) for g in genotypes]

    # Turn the unique bit sequences array into a list of tuples with the bit sequence and its corresponding fitness
    # The tuples can still be used as nodes because they are hashable objects
    genotypes = [(genotypes[i], fitness[i]) for i in range(len(genotypes))]

    # Build hierarchical structure for N-bit sequences that differ by 1 bit at each level
    hierarchy = [[] for i in range(N+1)]
    for g in genotypes: hierarchy[g[0].count("1")].append(g)

    # Add all unique bit sequences as nodes to the graph
    G = nx.DiGraph()
    G.add_nodes_from(genotypes)

    # Add edges with appropriate weights depending on the TM
    sf = 5 # edge thickness scale factor
    TM = p.random_mutations(len(genotypes))
    for i in range(len(TM)):
        for j in range(len(TM[i])):
            if TM[i][j] != 0 and i != j:
                G.add_edge(genotypes[i], genotypes[j], weight=1)
    

    # just using spring layout to generate an initial dummy pos dict
    pos = nx.spring_layout(G)

    # # calculate how many entires in the longest row, it will be N choose N/2
    # # because the longest row will have every possible way of putting N/2 1s (or 0s) into N bits
    maxLen = math.factorial(N) / math.factorial(N//2)**2

    # Position the nodes in a layered hierarchical structure by modifying pos dict
    y = 1
    for row in hierarchy:
        if len(row) > maxLen: maxLen = len(row)
    for i in range(len(hierarchy)):
        levelLen = len(hierarchy[i])
        # algorithm for horizontal spacing.. may not be 100% correct?
        offset = (maxLen - levelLen + 1) / maxLen
        xs = np.linspace(0 + offset / 2, 1 - offset / 2, levelLen)
        for j in range(len(hierarchy[i])):
            pos[hierarchy[i][j]] = (xs[j], y)
            # labels[hierarchy[i][j]] = hierarchy[i][j][0]
        y -= 1 / N

    node_size = 800
    
    labels = dict(pos)
    for k in labels.keys():
        labels[k] = k[0]
    
    # # Draw the graph
    plt.axis('off')
    cmap='plasma'
    
    nx.draw(G, pos, with_labels=False, linewidths=1, node_color=fitness,
            node_size=node_size,arrows=False,
            vmin = min(fitness), vmax=max(fitness),cmap=cmap)
    nx.draw_networkx_labels(G,pos,labels,font_size=10,font_color='red')
    
    # node_colors = 
    # pc = mpl.collections.PatchCollection(edges, cmap=cmap)
    # pc.set_array(edge_colors)
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = min(fitness), vmax=max(fitness)))
    sm._A = []
    cb = plt.colorbar(sm,drawedges=False)
    cb.outline.set_visible(False)
    
    ax = plt.gca()
    return ax