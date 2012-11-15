from tarmii.theme.tests.base import TarmiiThemeTestBase

class TestVideosView(TarmiiThemeTestBase):
    """ Test Videos browser view
    """

    def test_videos(self):
        view = self.videos.restrictedTraverse('@@videos')
        import pdb; pdb.set_trace()
        batch = view.videos()
        self.assertEquals([self.vid1thumb,self.vid2thumb],
                          [p.getObject() for p in batch])

    def test_add_video_button_path(self):
        view = self.videos.restrictedTraverse('@@videos')
        self.assertEqual(view.add_video_button_path(), 
                         "%s/createObject?type_name=File" %
                         self.videos.absolute_url())
