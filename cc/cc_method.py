class CCMethod(object):
    pass

    @staticmethod
    def is_chinese(string):
        """判断是否有中文
        :param     string(str):所有字符串
        :returns   :False
        :raises    error:
        """
        for ch in string:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False


if __name__ == '__main__':
    pass
    cc = CCMethod.is_chinese("中")
    print(cc)
    cc = CCMethod.is_chinese("a")
    print(cc)