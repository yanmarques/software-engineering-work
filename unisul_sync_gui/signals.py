from pydispatch import dispatcher 


class pysignal:
    def emit(self, 
             sender=dispatcher.Any,
             *args, 
             **kwargs):
        dispatcher.send(signal=self, 
                        sender=sender, 
                        *args, 
                        **kwargs)

    def connect(self, *args, **kwargs):
        dispatcher.connect(*args, signal=self, **kwargs)


class _signals:
    # app life cycle
    opening = pysignal()
    closing = pysignal()
    started = pysignal()

    showing = pysignal()
    shown = pysignal()
    
    item_completed = pysignal()
