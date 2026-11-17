# fast_pyplot.py
# Modo leve para matplotlib.pyplot sem mudar sua API.
# Mantém os MESMOS NOMES (plot, draw, pause, show, etc.), mas usa blitting e reuso de artistas.

import time
from collections import defaultdict

def patch_pyplot(plt):
    """
    Aplique após importar pyplot:
        import matplotlib.pyplot as plt
        from fast_pyplot import patch_pyplot
        patch_pyplot(plt)
    """
    import matplotlib
    # Garanta um backend interativo adequado
    try:
        backend = matplotlib.get_backend()
        # Se for non-interactive, tenta um interativo comum
        if backend.lower() in ("agg", "pdf", "svg", "ps", "cairo"):
            matplotlib.use("TkAgg", force=True)
    except Exception:
        pass

    # Ativa modo interativo (evita travas de UI)
    plt.ion()

    # Guardar originais para fallback quando necessário
    _orig = {
        "plot": plt.plot,
        "draw": plt.draw,
        "pause": plt.pause,
        "clf": plt.clf,
        "cla": plt.cla,
        "xlim": plt.xlim,
        "ylim": plt.ylim,
        "autoscale": getattr(plt, "autoscale", None),
        "figure": plt.figure,
        "subplots": getattr(plt, "subplots", None),
        "gca": plt.gca,
        "gcf": plt.gcf,
        "show": plt.show,
    }

    # Estado por eixo para blitting
    _state = defaultdict(lambda: {"bg": None, "artists": set(), "need_bg": True})

    # Utilitários internos
    def _all_axes():
        figs = list(map(plt.figure, plt.get_fignums()))
        for f in figs:
            for ax in f.axes:
                yield f, ax

    def _ensure_bg(fig, ax):
        st = _state[ax]
        canvas = fig.canvas
        if st["bg"] is None or st["need_bg"]:
            # Primeiro draw para rasterizar tudo que não é animado
            canvas.draw()
            st["bg"] = canvas.copy_from_bbox(ax.bbox)
            st["need_bg"] = False

    def _mark_bg_dirty(event=None):
        # Sempre que o figure é redesenhado (zoom, pan, resize), marcamos para recapturar BG
        fig = event.canvas.figure if event else None
        if fig:
            for ax in fig.axes:
                _state[ax]["need_bg"] = True
        else:
            for _, ax in _all_axes():
                _state[ax]["need_bg"] = True

    # Conectar eventos para manter BG coerente
    def _connect_draw_events(fig):
        if not hasattr(fig.canvas, "_fp_connected"):
            fig.canvas.mpl_connect("draw_event", _mark_bg_dirty)
            fig.canvas._fp_connected = True

    # Wrappers “leves”
    def light_figure(*args, **kwargs):
        fig = _orig["figure"](*args, **kwargs)
        _connect_draw_events(fig)
        return fig

    def light_subplots(*args, **kwargs):
        if _orig["subplots"] is None:
            # matplotlib muito antigo? fallback
            fig = light_figure()
            return fig, fig.add_subplot(111)
        fig, axs = _orig["subplots"](*args, **kwargs)
        _connect_draw_events(fig)
        return fig, axs

    def light_plot(*args, **kwargs):
        # Força animated=True por padrão (pode ser sobrescrito pelo usuário)
        kwargs.setdefault("animated", True)
        lines = _orig["plot"](*args, **kwargs)
        # Registrar artistas nos eixos correspondentes
        for line in lines:
            ax = line.axes
            _state[ax]["artists"].add(line)
        return lines

    def light_draw(*args, **kwargs):
        # Blit de todos os eixos conhecidos
        any_fig = False
        for fig, ax in _all_axes():
            any_fig = True
            _connect_draw_events(fig)
            _ensure_bg(fig, ax)

            st = _state[ax]
            canvas = fig.canvas

            # Restaura background daquele eixo
            canvas.restore_region(st["bg"])

            # Redesenha só os artistas animados
            for artist in list(st["artists"]):
                if artist.axes is not ax:
                    # artista mudou de eixo? limpa
                    st["artists"].discard(artist)
                    continue
                if not artist.get_visible():
                    continue
                ax.draw_artist(artist)

            # Blit apenas a área do eixo
            canvas.blit(ax.bbox)

        if any_fig:
            try:
                # Atualiza eventos pendentes
                fig.canvas.flush_events()
            except Exception:
                pass

    def light_pause(interval):
        # Redesenha rápido e respeita o tempo solicitado
        start = time.perf_counter()
        light_draw()
        remaining = interval - (time.perf_counter() - start)
        if remaining > 0:
            time.sleep(remaining)

    def light_xlim(*args, **kwargs):
        # Ajuste de limites invalida BG (precisamos recapturar)
        out = _orig["xlim"](*args, **kwargs)
        _mark_bg_dirty()
        return out

    def light_ylim(*args, **kwargs):
        out = _orig["ylim"](*args, **kwargs)
        _mark_bg_dirty()
        return out

    def light_autoscale(*args, **kwargs):
        if _orig["autoscale"] is not None:
            out = _orig["autoscale"](*args, **kwargs)
            _mark_bg_dirty()
            return out
        return None

    def light_clf():
        fig = _orig["gcf"]()
        # Limpa estado de todos os eixos da figura
        for ax in list(fig.axes):
            if ax in _state:
                del _state[ax]
        _orig["clf"]()
        _mark_bg_dirty()

    def light_cla():
        ax = _orig["gca"]()
        if ax in _state:
            del _state[ax]
        _orig["cla"]()
        _mark_bg_dirty()

    def light_show(*args, **kwargs):
        # show continua existindo, mas o desenho em tempo real vem do draw/pause
        return _orig["show"](*args, **kwargs)

    # Aplicar patches no módulo plt
    plt.figure = light_figure
    if _orig["subplots"] is not None:
        plt.subplots = light_subplots
    plt.plot = light_plot
    plt.draw = light_draw
    plt.pause = light_pause
    plt.xlim = light_xlim
    plt.ylim = light_ylim
    if _orig["autoscale"] is not None:
        plt.autoscale = light_autoscale
    plt.clf = light_clf
    plt.cla = light_cla
    plt.show = light_show

    # Opcional: tornar Line2D/PathCollection animados por padrão em outras chamadas comuns
    try:
        import matplotlib.lines as _ml
        _old_setdata = _ml.Line2D.set_data

        def _set_data_animated(self, *a, **k):
            # Se o usuário não marcou explicitamente, mantemos animated=True para render leve
            if self.get_animated() is False:
                self.set_animated(True)
            return _old_setdata(self, *a, **k)

        _ml.Line2D.set_data = _set_data_animated
    except Exception:
        pass
