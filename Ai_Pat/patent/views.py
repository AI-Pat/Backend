from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd



@swagger_auto_schema(
    method='get',
    operation_description="국가별 전체 동향 분석 API",
    responses={
        200: openapi.Response(
            description="성공적으로 분석한 결과를 반환합니다.",
        )
    }
)
@api_view(['GET'])
def country_trend(request):
    df = pd.read_excel('C:/preprocessed_and_statistics.xlsx', sheet_name='Statistics', header=0)

    # '출원일' 열에서 'sum' 텍스트를 포함하는 행 찾기
    sum_index = df[df['출원일'] == 'sum'].index[0]

    # 'sum' 행 바로 위의 데이터까지만 사용하여 출원년도 데이터 타입을 숫자로 변환
    df.loc[:sum_index - 1, '출원일'] = pd.to_numeric(df.loc[:sum_index - 1, '출원일'], errors='coerce')

    # A년과 B년 찾기
    min_year = df.loc[:sum_index - 1, '출원일'].min()
    max_year = df.loc[:sum_index - 1, '출원일'].max()

    # sum 행 선택
    sum_row = df.iloc[sum_index]

    # sum_row 내의 모든 값을 숫자로 변환 시도, 변환 불가능한 경우 NaN으로 설정
    sum_row_numeric = pd.to_numeric(sum_row, errors='coerce')
    max_country_code = sum_row_numeric.idxmax()
    specific_string = f"‘냉동김밥 제조장치’ 과제 기술과 관련된 {min_year}년부터 {max_year}년까지 전 세계 전체 특허출원 동향을 나타내는 것으로, 비교 대상 국가 중에 {max_country_code}의 출원 건수가 가장 높아 출원을 주도적으로 진행하고 있는 것으로 나타남."
    df = df[df['출원일'] != 'sum']

    response_data = {
        "title": "국가별 전체 동향",
        "data": {}
    }

    # 국가별로 데이터 처리
    for country in df.columns[1:]:  # 첫 번째 열은 '출원일', 따라서 국가명은 첫 번째 열 이후부터 시작
        x = df['출원일'].tolist()  # 출원일
        y = df[country].tolist()  # 해당 국가의 출원 건수

        # 각 국가별로 x, y 데이터를 새로운 형태로 저장
        transformed_data = []
        for year, count in zip(x, y):
            # NaN 값 또는 유효하지 않은 데이터는 무시
            if pd.notnull(year) and pd.notnull(count):
                transformed_data.append({"x": year, "y": count})

        response_data["data"][country] = transformed_data

    response_data["content"] = specific_string

    return Response(response_data)

@swagger_auto_schema(
    method='get',
    operation_description="국가별 출원 동향 API",
    responses={
        200: openapi.Response('성공적인 데이터 반환', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'KR': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description='한국 출원 동향 제목'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='출원일과 출원 수 데이터',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'x': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원일'),
                                    'y': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원 수'),
                                }
                            )
                        ),
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description='한국 출원 동향 요약'),
                    }
                ),
                'JP': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description='일본 출원 동향 제목'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='출원일과 출원 수 데이터',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'x': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원일'),
                                    'y': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원 수'),
                                }
                            )
                        ),
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description='일본 출원 동향 요약'),
                    }
                ),
                'US': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description='미국 출원 동향 제목'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='출원일과 출원 수 데이터',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'x': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원일'),
                                    'y': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원 수'),
                                }
                            )
                        ),
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description='미국 출원 동향 요약'),
                    }
                ),
                'CN': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(type=openapi.TYPE_STRING, description='중국 출원 동향 제목'),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='출원일과 출원 수 데이터',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'x': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원일'),
                                    'y': openapi.Schema(type=openapi.TYPE_INTEGER, description='출원 수'),
                                }
                            )
                        ),
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description='중국 출원 동향 요약'),
                    }
                ),
            },
            description='각 국가별 출원 동향 데이터'
        ))
    }
)
@api_view(['GET'])
def countrywise_trend(request):
    # 데이터셋 로드
    df = pd.read_excel('C:/preprocessed_and_statistics.xlsx', sheet_name='Statistics', header=0)

    european_countries = [
        'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
        'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE',
        'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL',
        'MK', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI',
        'ES', 'SE', 'CH', 'UA', 'GB', 'VA'
    ]

    # '출원일' 열에서 'sum' 텍스트를 포함하는 행 찾기
    sum_index = df[df['출원일'] == 'sum'].index[0]

    # 'sum' 행 바로 위의 데이터까지만 사용하여 출원년도 데이터 타입을 숫자로 변환
    df.loc[:sum_index - 1, '출원일'] = pd.to_numeric(df.loc[:sum_index - 1, '출원일'], errors='coerce')

    # A년과 B년 찾기
    min_year = df.loc[:sum_index - 1, '출원일'].min()
    max_year = df.loc[:sum_index - 1, '출원일'].max()

    # sum 행 선택
    sum_row = df.iloc[sum_index]

    # sum_row 내의 모든 값을 숫자로 변환 시도, 변환 불가능한 경우 NaN으로 설정
    sum_row_numeric = pd.to_numeric(sum_row, errors='coerce')

    # NaN 값을 제외하고 최대값을 가진 열의 이름 찾기
    max_country_code = sum_row_numeric.idxmax()

    sum_row['EP'] = sum([sum_row[code] for code in european_countries if code in sum_row])
    total_applications = sum_row_numeric.dropna().sum()

    # 일본(JP), 미국(US), 한국(KR)의 출원 건수 비율 계산
    jp_percentage = int((sum_row['JP'] / total_applications) * 100)
    us_percentage = int((sum_row['US'] / total_applications) * 100)
    kr_percentage = int((sum_row['KR'] / total_applications) * 100)
    cn_percentage = int((sum_row['CN'] / total_applications) * 100)
    # ep_percentage = int((sum_row['EP'] / total_applications) * 100)

    # 'sum' 행을 제외
    df = df[df['출원일'] != 'sum']

    # '출원일'을 기준으로 오름차순 정렬
    df.sort_values(by='출원일', inplace=True)

    # 결과를 저장할 딕셔너리 생성
    result = {}

    country_codes = ['KR', 'JP', 'US', 'CN']

    # 각 국가별로 데이터 처리
    for code in country_codes:
        # 해당 국가의 출원일과 출원 수 데이터 추출
        x = df['출원일'].tolist()  # 출원일
        y = df[code].tolist()  # 해당 국가의 출원 수

        # 결과 딕셔너리에 저장
        result[code] = {
            'title': f'국가별 동향({code}) ',
            'data': [{'x': date, 'y': count} for date, count in zip(x, y)],
            'content': ''
        }

        if code == 'JP':
            result[code]['content'] = f'일본은 전체 출원 건수의 {jp_percentage}%로, 분석기간 동안 증감을 반복하며, 전체적으로는 감소하는 추세를 나타내고 있음.'
        elif code == 'US':
            result[code][
                'content'] = f'미국은 전체 출원 건수의 {us_percentage}%를 차지하고 있으며, {min_year}년도 부터 증가세를 보이며, 현재까지 증감을 반복하며 출원하고 있음.'
        elif code == 'KR':
            result[code][
                'content'] = f'한국은 전체 출원 건수의 {kr_percentage}%, 전체 건수 중 가장 많은 점유율을 가지며, 분석기간 동안 증감을 반복하며 출원하고 있음.'
        elif code == 'CN':
            result[code][
                'content'] = f'중국은 전체 출원 건수의 {cn_percentage}%, 분섐기간 초반부터 증가세를 보이며, 2015년까지 증가, 이후 점차적으로 감소세를 나타내고 있음.'
    converted_results = []

    # 기존 결과 딕셔너리에서 데이터 추출 및 변환
    for code, details in result.items():
        # 각 국가별 데이터를 새로운 형식으로 변환
        new_format = {
            'title': details['title'].replace('국가별 동향', '국가별 동향').strip(),
            'data': details['data'],
            'content': details['content']
        }

        # 변환된 데이터를 리스트에 추가
        converted_results.append(new_format)
    # JSON 형태로 반환
    return Response(converted_results)


@swagger_auto_schema(
    method='get',
    operation_description="연도별 전체 동향 조회 API",
    responses={
        200: openapi.Response(
            description='연도별 전체 동향 조회 성공',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'title': openapi.Schema(type=openapi.TYPE_STRING, description='제목'),
                    'data': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description='연도별 데이터 리스트',
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'x': openapi.Schema(type=openapi.TYPE_INTEGER, description='연도'),
                                'y': openapi.Schema(type=openapi.TYPE_INTEGER, description='총계'),
                            }
                        )
                    ),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, description='설명'),
                }
            )
        )
    }
)
@api_view(['GET'])
def ytd_trend(request):
    df = pd.read_excel('C:/preprocessed_and_statistics.xlsx', sheet_name='Statistics', header=0)

    # '출원일' 열에서 'sum' 텍스트를 포함하는 행 찾기
    sum_index = df[df['출원일'] == 'sum'].index[0]

    # 'sum' 행 바로 위의 데이터까지만 사용하여 출원년도 데이터 타입을 숫자로 변환
    df.loc[:sum_index - 1, '출원일'] = pd.to_numeric(df.loc[:sum_index - 1, '출원일'], errors='coerce')

    # A년과 B년 찾기
    min_year = df.loc[:sum_index - 1, '출원일'].min()
    max_year = df.loc[:sum_index - 1, '출원일'].max()
    specific_string = f"{min_year}년부터 {max_year}년까지 ‘냉동김밥 제조장치’ 과제 기술과 관련된 전세계 출원건수 동향 및 누적건수를 나타내는 것으로, {min_year}년부터 {max_year}년도까지 증감을 반복하는 양상을 보임. 국내외 모두 냉동 간편식 중심으로 시장이 큰 폭으로 증가하고 있는 추세로, 관련 기술의 출원건수도 큰 폭으로 증가할 것으로 판단되며, 미공개 특허가 존재하는 것을 감안하여 출원 추이를 모니터링할 필요가 있음."

    # 'sum' 행 이하 데이터를 제외하고 연도별 합계 계산
    df_numeric = df.loc[:sum_index - 1, df.columns != '출원일']
    yearly_sums = df_numeric.sum(axis=1)

    # 연도별 합계를 DataFrame에 추가 (예시에서는 'Total'이라는 새 컬럼에 저장)
    df.loc[:sum_index - 1, 'Total'] = yearly_sums

    # DataFrame을 '출원일' 기준으로 오름차순 정렬
    df_sorted = df.loc[:sum_index - 1].sort_values(by='출원일')

    x = df_sorted['출원일']
    y = df_sorted['Total']

    data_list = [{"x": year, "y": total} for year, total in zip(list(x), list(y))]
    # 결과를 JSON 형태로 반환
    response_data = {
        "title": "연도별 전체 동향",
        "data": data_list,
        "content": specific_string
    }

    return Response(response_data)
