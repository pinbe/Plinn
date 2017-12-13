from zope.interface import Interface


class ILayeredDocument(Interface) :

    def layersStack() :
        """
        Returns all layers wrapped inside <div>s.
        :return: html string
        """