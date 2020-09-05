"""
Home Climate Monitoring

author: GiantMolecularCloud

This script is part of a collection of scripts to log climate information in python and send them
to influxdb and graphana for plotting.

Development script to gather data from influxdb and analysize them statistically. This script provides
the methods to plot nice 2D histograms with marginalizations over both dimensions.
"""

def plot_hist2d(x,y):
    import matplotlib.pyplot as plt

    def setup_figure(figsize=(6,6)):
        from matplotlib.gridspec import GridSpec
        fig = plt.figure(figsize=figsize)
        gs  = GridSpec(3,3)
        gs.update(left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.0, wspace=0.0)
        ax_hist2d = plt.subplot(gs[1:,:-1])
        ax_histx  = plt.subplot(gs[0,:-1], sharex=ax_hist2d)
        ax_histy  = plt.subplot(gs[1:,-1], sharey=ax_hist2d)
        ax_corner = plt.subplot(gs[0,-1])
        return fig,gs,ax_hist2d,ax_histx,ax_histy,ax_corner

    def alpha_cmap(cmap):
        import numpy as np
        cmap_a = cmap(np.arange(cmap.N))
        cmap_a[:,-1] = np.linspace(0, 1, cmap.N)
        return ListedColormap(cmap_a)

    def add_hist2d():
        hist2d = ax_hist2d.imshow(histograms2D[x+' '+y]['histogram'].transpose(),            # need to swap axes to display with imshow
                                  cmap   = cmap,
                                  extent = [hsetup[x]['min'],hsetup[x]['max'],hsetup[y]['min'],hsetup[y]['max']],
                                  aspect = 'auto',
                                  origin = 'lower',
                                  zorder = 5
                                 )
        # return hist2d

    def add_histx():
        for r,a in ranges.items():
            hist_x = ax_histx.plot(histograms[x][r]['edges'][:-1],
                                   histograms[x][r]['histogram'],
                                   drawstyle = 'steps-post',
                                   linewidth = 1,
                                   color     = colors[x],
                                   alpha     = a['alpha']
                                  )
        # return hist_x

    def add_histy():
        for r,a in ranges.items():
            hist_y = ax_histy.plot(histograms[y][r]['histogram'],
                                   histograms[y][r]['edges'][:-1],
                                   drawstyle = 'steps-post',
                                   linewidth = 1,
                                   color     = colors[y],
                                   alpha     = a['alpha']
                                  )
        # return hist_y

    def add_legend():
        from matplotlib.lines import Line2D
        sorted_ranges = sorted(ranges.items(), key=lambda item: item[1]['alpha'], reverse=True)
        leg_lines = [Line2D([0], [0], color='k', alpha=a['alpha'], lw=1) for r,a in sorted_ranges]
        ax_corner.legend(leg_lines, [r[0] for r in sorted_ranges], frameon=False)

    def format_ax_hist2d():
        ax_hist2d.xaxis.set_tick_params(direction='in', top=True, bottom=True)
        ax_hist2d.yaxis.set_tick_params(direction='in', left=True, right=True)
        ax_hist2d.set_xlabel(hsetup[x]['label'])
        ax_hist2d.set_ylabel(hsetup[y]['label'])

    def add_grid(ax):
        ax.set_axisbelow(True)
        ax.grid(ls=':', c='lightgrey')

    def hide_labels(ax):
        if ax==ax_corner:
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
        if ax==ax_histx:
            ax.yaxis.set_visible(False)
            ax.tick_params(axis='x', which='both', top=False, bottom=False, labeltop=False, labelbottom=False)
        if ax==ax_histy:
            ax.xaxis.set_visible(False)
            ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=False, labelright=False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

    # build figure
    fig,gs,ax_hist2d,ax_histx,ax_histy,ax_corner = setup_figure()
    cmap = alpha_cmap(plt.cm.gist_heat_r)
    add_hist2d()
    add_histx()
    add_histy()
    format_ax_hist2d()
    for ax in [ax_histx,ax_histy,ax_corner]:
        hide_labels(ax)
    for ax in [ax_hist2d,ax_histx,ax_histy]:
        add_grid(ax)
    add_legend()
    fig.savefig('/home/pi/homeclimate/statistics/histogram_'+x+'_'+y+'.pdf', dpi=300, bbox_inches='tight')
