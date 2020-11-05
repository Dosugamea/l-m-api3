class Message(object):
    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)


class TextMessage(Message):
    def __init__(self, text):
        self.type = "text"
        self.text = text


class StickerMessage(Message):
    def __init__(self, packageId, stickerId):
        self.type = "sticker"
        self.packageId = str(packageId)
        self.stickerId = str(stickerId)


class ImageMessage(Message):
    def __init__(self, originalContentUrl, previewImageUrl=None):
        self.type = "image"
        self.originalContentUrl = originalContentUrl
        if previewImageUrl is not None:
            self.previewImageUrl = previewImageUrl
        else:
            self.previewImageUrl = originalContentUrl


class VideoMessage(Message):
    def __init__(self, originalContentUrl, previewImageUrl=None):
        self.type = "video"
        self.originalContentUrl = originalContentUrl
        if previewImageUrl is not None:
            self.previewImageUrl = previewImageUrl
        else:
            self.previewImageUrl = originalContentUrl


class LocationMessage(Message):
    def __init__(self, title, address, latitude, longitude):
        self.type = "location"
        self.title = title
        self.address = address
        self.latitude = latitude
        self.longitude = longitude


class TemplateMessage(Message):
    def __init__(self, template, altText="template message"):
        self.type = "template"
        self.template = template
        self.altText = altText


class FlexMessage(Message):
    def __init__(self, contents, altText="flex message"):
        self.type = "flex"
        self.contents = contents
        self.altText = altText
