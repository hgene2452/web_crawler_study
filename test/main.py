import unittest

class VerboseTestResult(unittest.TextTestResult):
    def startTest(self, test):
        # 테스트 시작 시 테스트 이름 출력
        print(f"\n->\t[테스트 시작] {test}")
        super().startTest(test)

def main():
    # 루트 디렉터리에서 실행한다고 가정. test 폴더내에서 테스트를 찾도록 start_dir 설정
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(top_level_dir=".", start_dir="./test", pattern="*_test.py")

    # 커스텀 테스트 러너 사용
    test_runner = unittest.TextTestRunner(resultclass=VerboseTestResult)
    test_runner.run(test_suite)

if __name__ == "__main__":
    main()