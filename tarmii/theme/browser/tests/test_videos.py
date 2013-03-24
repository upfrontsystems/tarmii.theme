from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestVideosView(TarmiiThemeTestBase):
    """ Test Videos browser view
    """

    def test_videos(self):
        view = self.videos.restrictedTraverse('@@videos')
        batch = view.videos()
        self.assertEquals([self.vid1thumb,self.vid2thumb],
                          [p.getObject() for p in batch])

        self.request.set('category', "howto")
        batch = view.videos()
        self.assertEquals([self.vid1thumb,self.vid2thumb],
                          [p.getObject() for p in batch])

        self.request.set('category', "pedagogic")
        batch = view.videos()
        self.assertEquals([],[p.getObject() for p in batch])

        self.request.set('category', "")
        self.request.cookies['VIDEO_PAGE'] = ''
        batch = view.videos()
        self.assertEquals([self.vid1thumb,self.vid2thumb],
                          [p.getObject() for p in batch])

        self.request.set('category', "")
        self.request.response.setCookie("VIDEO_PAGE", 'Howto')
        self.request.cookies['VIDEO_PAGE'] = 'Howto'
        batch = view.videos()
        self.assertEquals([self.vid1thumb,self.vid2thumb],
                          [p.getObject() for p in batch])

        self.request.set('category', "")
        self.request.response.setCookie("VIDEO_PAGE", 'Anything')
        self.request.cookies['VIDEO_PAGE'] = 'Anything'
        batch = view.videos()
        self.assertEquals([],[p.getObject() for p in batch])

    def test_addvideo_visible(self):
        view = self.videos.restrictedTraverse('@@videos')
        self.assertEquals(view.addvideo_visible(),True)
        
    def test_user_is_admin(self):
        view = self.videos.restrictedTraverse('@@videos')
        self.assertEquals(view.user_is_admin(),True)

    def test_display_howto_videos(self):
        view = self.videos.restrictedTraverse('@@videos')

        self.request.set('category', "howto")
        self.assertEquals(view.display_howto_videos(),True)
        self.request.set('category', "pedagogic")
        self.assertEquals(view.display_howto_videos(),False)

        self.request.set('category', "")
        self.request.cookies['VIDEO_PAGE'] = ''
        self.assertEquals(view.display_howto_videos(),True)
        self.request.cookies['VIDEO_PAGE'] = 'Howto'
        self.assertEquals(view.display_howto_videos(),True)
        self.request.cookies['VIDEO_PAGE'] = 'Anything'
        self.assertEquals(view.display_howto_videos(),False)


class TestVideoView(TarmiiThemeTestBase):
    """ Test Video browser view
    """

    def test_video_link(self):
        view = self.videos.restrictedTraverse('@@video')
        self.assertEqual(view.video_link(),
                         "%s/at_download/file" % self.videos.absolute_url())
