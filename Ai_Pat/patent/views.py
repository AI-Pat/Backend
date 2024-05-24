from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from django.http import JsonResponse
import os


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

    # 일본(JP), 미국(US), 한국(KR), 중국(CN)의 출원 건수 비율 계산
    jp_percentage = int((sum_row['JP'] / total_applications) * 100)
    us_percentage = int((sum_row['US'] / total_applications) * 100)
    kr_percentage = int((sum_row['KR'] / total_applications) * 100)
    cn_percentage = int((sum_row['CN'] / total_applications) * 100)

    # 'sum' 행을 제외
    df = df[df['출원일'] != 'sum']

    # '출원일'을 기준으로 오름차순 정렬
    df.sort_values(by='출원일', inplace=True)

    # 결과를 저장할 딕셔너리 생성
    result = []

    country_codes = ['KR', 'JP', 'US', 'CN']

    # 각 국가별로 데이터 처리
    for code in country_codes:
        # 해당 국가의 출원일과 출원 수 데이터 추출
        x = df['출원일'].tolist()  # 출원일
        y = df[code].tolist()  # 해당 국가의 출원 수

        # 국가별 데이터 변환
        data = [{'x': date, 'y': count, 'category': code.lower()} for date, count in zip(x, y)]

        # content 작성
        if code == 'JP':
            content = f'일본은 전체 출원 건수의 {jp_percentage}%로, 분석기간 동안 증감을 반복하며, 전체적으로는 감소하는 추세를 나타내고 있음.'
        elif code == 'US':
            content = f'미국은 전체 출원 건수의 {us_percentage}%를 차지하고 있으며, {min_year}년도 부터 증가세를 보이며, 현재까지 증감을 반복하며 출원하고 있음.'
        elif code == 'KR':
            content = f'한국은 전체 출원 건수의 {kr_percentage}%, 전체 건수 중 가장 많은 점유율을 가지며, 분석기간 동안 증감을 반복하며 출원하고 있음.'
        elif code == 'CN':
            content = f'중국은 전체 출원 건수의 {cn_percentage}%, 분석기간 초반부터 증가세를 보이며, 2015년까지 증가, 이후 점차적으로 감소세를 나타내고 있음.'

        # 국가별 결과 딕셔너리에 저장
        result.append({
            'main_title': '전체 동향',
            'title': f'국가별 전체 동향({code.lower()})',
            'data': data,
            'content': content
        })

    # JSON 형태로 반환
    return Response(result)


@api_view(['GET'])
def applicant_trend_by_country(request):
    df = pd.read_excel('C:/preprocessed_and_statistics.xlsx', sheet_name='Statistics', header=0)

    # 유럽 국가 코드 목록
    european_countries = [
        'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
        'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE',
        'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL',
        'MK', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI',
        'ES', 'SE', 'CH', 'UA', 'GB', 'VA'
    ]

    # 처리할 국가 코드 목록
    country_codes = ['KR', 'EU', 'JP', 'US']

    # 결과를 저장할 딕셔너리
    response_data = {}

    for country_code in country_codes:
        if country_code == 'KR':
            df_filtered = df[df['출원인국가'] == country_code]
            # 한국의 경우 외국 국적 출원인 비율 계산
            foreign_applicants = df_filtered[df_filtered['출원인국가'].isin(european_countries + ['JP', 'US'])]
            foreign_applicants_ratio = foreign_applicants['출원인'].value_counts(normalize=True) * 100
        elif country_code == 'EU':
            df_filtered = df[df['출원인국가'].isin(european_countries)]
            foreign_applicants_ratio = None  # 유럽의 경우 별도의 외국 국적 출원인 비율 계산은 하지 않음
        else:
            df_filtered = df[df['출원인국가'] == country_code]
            foreign_applicants_ratio = None

        # 출원인 동향 계산
        trend = df_filtered['출원인'].value_counts()

        # 결과 데이터 준비
        data_list = [{"출원인": applicant, "건수": count} for applicant, count in trend.items()]

        response_data[country_code] = {
            "main_title": f"{country_code} 국가별 출원인 동향",
            "data": data_list,
            "foreign_applicants_ratio": foreign_applicants_ratio.to_dict() if foreign_applicants_ratio is not None else "해당 사항 없음"
        }

    return Response(response_data)

@api_view(['GET'])
def countrywise_trend_all(request):
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

    # 일본(JP), 미국(US), 한국(KR), 중국(CN)의 출원 건수 비율 계산
    jp_percentage = int((sum_row['JP'] / total_applications) * 100)
    us_percentage = int((sum_row['US'] / total_applications) * 100)
    kr_percentage = int((sum_row['KR'] / total_applications) * 100)
    cn_percentage = int((sum_row['CN'] / total_applications) * 100)

    # 'sum' 행을 제외
    df = df[df['출원일'] != 'sum']

    # '출원일'을 기준으로 오름차순 정렬
    df.sort_values(by='출원일', inplace=True)

    # 결과를 저장할 딕셔너리 생성
    result = []

    country_codes = ['KR', 'JP', 'US', 'CN']

    # 각 국가별로 데이터 처리
    for code in country_codes:
        # 해당 국가의 출원일과 출원 수 데이터 추출
        x = df['출원일'].tolist()  # 출원일
        y = df[code].tolist()  # 해당 국가의 출원 수

        # 국가별 데이터 변환
        data = [{'x': date, 'y': count, 'category': code.lower()} for date, count in zip(x, y)]

        # content 작성
        if code == 'JP':
            content = f'일본은 전체 출원 건수의 {jp_percentage}%로, 분석기간 동안 증감을 반복하며, 전체적으로는 감소하는 추세를 나타내고 있음.'
        elif code == 'US':
            content = f'미국은 전체 출원 건수의 {us_percentage}%를 차지하고 있으며, {min_year}년도 부터 증가세를 보이며, 현재까지 증감을 반복하며 출원하고 있음.'
        elif code == 'KR':
            content = f'한국은 전체 출원 건수의 {kr_percentage}%, 전체 건수 중 가장 많은 점유율을 가지며, 분석기간 동안 증감을 반복하며 출원하고 있음.'
        elif code == 'CN':
            content = f'중국은 전체 출원 건수의 {cn_percentage}%, 분석기간 초반부터 증가세를 보이며, 2015년까지 증가, 이후 점차적으로 감소세를 나타내고 있음.'
        specific_string = f"‘냉동김밥 제조장치’ 과제 기술과 관련된 {min_year}년부터 {max_year}년까지 전 세계 전체 특허출원 동향을 나타내는 것으로, 비교 대상 국가 중에 {max_country_code}의 출원 건수가 가장 높아 출원을 주도적으로 진행하고 있는 것으로 나타남."
        # 국가별 결과 딕셔너리에 저장
        result.append({
            'main_title': '전체 동향',
            'title': f'국가별 전체 동향({code.lower()})',
            'data': data,
        })
    result.append({
        'content': specific_string
    })
    # JSON 형태로 반환
    return Response(result)

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
        "main_title": "전체 동향",
        "title": "연도별 전체 동향",
        "data": data_list,
        "content": specific_string
    }

    return Response(response_data)


# @api_view(['GET'])
# def applicant_trend_by_country(request):
#     df = pd.read_excel('C:/preprocessed_and_statistics.xlsx', sheet_name='Preprocessed Data', header=0)
#
#     # 유럽 국가 코드 목록
#     european_countries = [
#         'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
#         'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE',
#         'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL',
#         'MK', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI',
#         'ES', 'SE', 'CH', 'UA', 'GB', 'VA'
#     ]
#
#     # 분석할 국가 목록
#     country_codes = ['KR', 'EU', 'JP', 'US']
#
#     # 결과를 저장할 딕셔너리
#     response_data = {}
#
#     for country_code in country_codes:
#         if country_code == 'KR':
#             df_filtered = df[df['출원인국가'] == country_code]
#             # 한국의 경우 외국 국적 출원인 비율 계산
#             foreign_applicants = df_filtered[~df_filtered['출원인국가'].isin(['KR'])]
#             foreign_applicants_ratio = foreign_applicants['출원인'].value_counts(normalize=True) * 100
#         elif country_code == 'EU':
#             df_filtered = df[df['출원인국가'].isin(european_countries)]
#             # 유럽의 경우 외국 국적 출원인 비율 계산
#             foreign_applicants = df_filtered[~df_filtered['출원인국가'].isin(european_countries)]
#             foreign_applicants_ratio = foreign_applicants['출원인'].value_counts(normalize=True) * 100
#         elif country_code == 'JP':
#             df_filtered = df[df['출원인국가'] == country_code]
#             # 일본의 경우 외국 국적 출원인 비율 계산
#             foreign_applicants = df_filtered[~df_filtered['출원인국가'].isin(['JP'])]
#             foreign_applicants_ratio = foreign_applicants['출원인'].value_counts(normalize=True) * 100
#         elif country_code == 'US':
#             df_filtered = df[df['출원인국가'] == country_code]
#             # 미국의 경우 외국 국적 출원인 비율 계산
#             foreign_applicants = df_filtered[~df_filtered['출원인국가'].isin(['US'])]
#             foreign_applicants_ratio = foreign_applicants['출원인'].value_counts(normalize=True) * 100
#
#         # 출원인 동향 계산
#         trend = df_filtered['출원인'].value_counts()
#
#         # 결과 데이터 준비
#         data_list = [{"출원인": applicant, "건수": count} for applicant, count in trend.items()]
#
#         response_data[country_code] = {
#             "main_title": f"{country_code} 국가별 출원인 동향",
#             "data": data_list,
#             "foreign_applicants_ratio": foreign_applicants_ratio.to_dict() if not foreign_applicants_ratio.empty else "해당 사항 없음"
#         }
#
#     return Response(response_data)
# @api_view(['GET'])
# def applicant_trend_by_country(request):
#
#     # 엑셀 파일 읽기
#     df = pd.read_excel('C:/preprocessed_and_statistics.xlsx', sheet_name='Preprocessed Data', header=0)
#
#     # 유럽 국가 코드 목록
#     european_countries = [
#         'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
#         'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE',
#         'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL',
#         'MK', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI',
#         'ES', 'SE', 'CH', 'UA', 'GB', 'VA'
#     ]
#
#     # 유럽 국가 데이터 필터링
#     df_europe = df[df['출원인국가'].isin(european_countries)]
#
#     # 전체 건수 대비 유럽 국가 출원인의 비율 계산
#     total_applicants_count = len(df)
#     european_applicants_count = len(df_europe)
#     european_applicants_ratio = (european_applicants_count / total_applicants_count) * 100
#     non_european_applicants_ratio = 100 - european_applicants_ratio
#
#     # 연도별 출원 건수 계산
#     trend = df_europe.groupby('출원일')['출원인'].count()
#
#     # 결과 데이터 준비
#     data_list = [{"x": year, "y": count, "category": "ep"} for year, count in trend.items()]
#
#     response_data = {
#         "main_title": "국가별 동향 분석",
#         "title": "국가별 출원일 동향(EP)",
#         "data": data_list,
#         "content": f"유럽 국가 출원인은 전체 출원 건수의 {european_applicants_ratio:.2f}%, 나머지 국가 출원인은 {non_european_applicants_ratio:.2f}%입니다."
#     }
#
#     return Response(response_data)
@api_view(['GET'])
def applicant_trend_by_country(request):
    # 엑셀 파일 읽기
    df = pd.read_excel('C:/preprocessed_and_statistics.xlsx', sheet_name='Preprocessed Data', header=0)

    # 국가 코드 목록 정의
    countries = {
        'EU': [
            'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ',
            'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU', 'IS', 'IE',
            'IT', 'LV', 'LI', 'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL',
            'MK', 'NO', 'PL', 'PT', 'RO', 'RU', 'SM', 'RS', 'SK', 'SI',
            'ES', 'SE', 'CH', 'UA', 'GB', 'VA'
        ],
        'KR': ['KR'],
        'JP': ['JP'],
        'US': ['US'],
        'CN': ['CN']
    }

    # 결과 데이터 준비
    response_data = {
        "main_title": "국가별 동향 분석",
        "content": [],
        "data": []
    }

    total_applicants_count = len(df)

    for country_group, country_codes in countries.items():
        # 해당 국가 그룹 데이터 필터링
        df_country = df[df['출원인국가'].isin(country_codes)]

        # 해당 국가 그룹의 출원인 비율 계산
        country_applicants_count = len(df_country)
        country_applicants_ratio = (country_applicants_count / total_applicants_count) * 100

        # 연도별 출원 건수 계산
        trend = df_country.groupby('출원일')['출원인'].count()

        # 데이터 리스트에 추가
        data_list = [{"x": year, "y": count, "category": country_group} for year, count in trend.items()]
        response_data["data"].extend(data_list)

        # 내용 추가
        response_data["content"].append(
            f"{country_group} 국가 출원인은 전체 출원 건수의 {country_applicants_ratio:.2f}%입니다."
        )

    return Response(response_data)
@csrf_exempt
def upload_preprocess_statistics(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        # 파일 저장 경로 설정
        file_path = os.path.join('C:/Users/kbo00/Downloads', myfile.name)

        # 파일 저장
        with open(file_path, 'wb+') as destination:
            for chunk in myfile.chunks():
                destination.write(chunk)

        # 엑셀 파일 로드
        df = pd.read_excel(file_path, engine='openpyxl')

        # 출원인이 없는 값 제거 (행 삭제)
        df.dropna(subset=['출원인'], inplace=True)

        # 출원인이 여러명인 경우 첫 번째 국가로 변경
        df['출원인국가'] = df['출원인국가'].apply(lambda x: x.split(',')[0] if ',' in x else x)

        # 출원인 대표 필드 값이 없으면 출원인으로 채우기
        df['출원인대표명'] = df.apply(lambda x: x['출원인'] if pd.isna(x['출원인대표명']) else x['출원인대표명'], axis=1)

        # 출원일 형식 변경 (년도만 남기기)
        df['출원일'] = df['출원일'].apply(lambda x: str(x).split('/')[0] if '/' in str(x) else str(x).split('.')[0])

        # 전처리된 데이터프레임 저장
        processed_file_path = 'C:/preprocessed_and_statistics.xlsx'
        with pd.ExcelWriter(processed_file_path) as writer:
            df.to_excel(writer, sheet_name='Preprocessed Data', index=False)

            # 출원일(년도)와 출원인국가를 기준으로 통계 생성
            statistics = df.groupby(['출원일', '출원인국가']).size().unstack(fill_value=0)

            # 각 국가별 합계 계산 및 정렬
            statistics['sum'] = statistics.sum(axis=1)
            statistics.sort_values(by='sum', ascending=False, inplace=True)
            statistics.drop(columns=['sum'], inplace=True)
            statistics.loc['sum'] = statistics.sum()

            # 합계가 큰 순서로 국가 열 정렬
            statistics = statistics[statistics.loc['sum'].sort_values(ascending=False).index]

            # 통계 표 저장
            statistics.to_excel(writer, sheet_name='Statistics')

        return JsonResponse({'message': '전처리 및 통계가 완료된 엑셀 파일이 저장되었습니다.'})
    else:
        return JsonResponse({'message': '파일을 업로드해주세요.'})