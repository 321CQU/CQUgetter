from datetime import datetime, date
from functools import reduce
from typing import Optional, Tuple, Dict, List, Union

from mycqu.course import CourseDayTime, CourseTimetable
from mycqu.exam import Exam
from mycqu.library import BookInfo
from mycqu.score import Score, GpaRanking
from mycqu.card import EnergyFees, Bill, Card


class CQUGetterParser:
    @staticmethod
    def parse_score_object(score: Score) -> Dict:
        return {'Term': str(score.session), 'Score': score.score, 'CourseCode': score.course.code,
                'CourseName': score.course.name, 'InstructorName': score.course.instructor,
                'Credit': score.course.credit, 'StudyNature': score.study_nature, 'CourseNature': score.course_nature}

    @staticmethod
    def parse_exam_object(exam: Exam) -> Dict:
        return {'Room': exam.room, 'StartTime': str(exam.start_time), 'EndTime': str(exam.end_time),
                'CourseName': exam.course.name, 'CourseCode': exam.course.code, 'SeatNum': exam.seat_num}

    @staticmethod
    def parse_course_day_time_object(course_day_time: CourseDayTime) -> Dict:
        if course_day_time is None:
            return {'WeekDay': None,
                    'Period': None}
        else:
            return {
                'WeekDay': course_day_time.weekday,
                'Period': CQUGetterParser._parse_two_params_tuple_to_str(course_day_time.period),
            }

    @staticmethod
    def parse_course_object(course: CourseTimetable) -> Dict:
        result = {'CourseCode': course.course.code,
                  'CourseName': course.course.name,
                  'RoomPosition': course.classroom,
                  'RoomName': course.classroom_name,
                  'InstructorName': course.course.instructor,
                  'Credit': course.course.credit,
                  'CourseNum': course.course.course_num,
                  'Weeks': CQUGetterParser._parse_weeks_to_str(list(
                      map(CQUGetterParser._parse_two_params_tuple_to_str, course.weeks))),
                  }
        result.update(CQUGetterParser.parse_course_day_time_object(course.day_time))
        return result

    @staticmethod
    def parse_gpa_ranking_object(gpa_ranking: GpaRanking) -> Dict:
        return {
            'GPA': gpa_ranking.gpa,
            'GradeRank': gpa_ranking.gradeRanking,
            'MajorRank': gpa_ranking.majorRanking,
            'ClassRank': gpa_ranking.classRanking,
        }

    @staticmethod
    def parse_energy_fee_object(energy_fee: EnergyFees, isHuXi: bool) -> Dict:
        if isHuXi:
            return {
                'Amount': energy_fee.balance,
                'Eamount': energy_fee.electricity_subsidy,
                'Wamount': energy_fee.water_subsidy,
            }
        else:
            return {
                'Amount': energy_fee.balance,
                'Subsidies': energy_fee.subsidies,
            }

    @staticmethod
    def parse_bill_object(bill: Bill) -> Dict:
        return {
            'Money': bill.tran_amount,
            'Location': bill.tran_place,
            'Time': bill.tran_date.strftime('%Y-%m-%d'),
            'Type': bill.tran_name
        }

    @staticmethod
    def parse_card_object(card: Card) -> Dict:
        return {
            'Amount': card.amount,
        }

    @staticmethod
    def parse_book_info_object(book_info: BookInfo) -> Dict:
        return {
            'Id': book_info.id,
            'Title': book_info.title,
            'CallNo': book_info.call_no,
            'BorrowTime': CQUGetterParser._parse_datetime_to_str(book_info.borrow_time),
            'ShouldReturnTime': CQUGetterParser._parse_date_to_str(book_info.should_return_time),
            'ReturnTime': CQUGetterParser._parse_date_to_str(book_info.return_time),
            'LibraryName': book_info.library_name,
            'RenewFlag': book_info.can_renew,
            'RenewCount': book_info.renew_count,
            'IsReturn': book_info.is_return,
        }


    @staticmethod
    def _parse_two_params_tuple_to_str(tuple: Optional[Tuple[int, int]]) -> str:
        if tuple is not None:
            return str(tuple[0]) + '-' + str(tuple[1])

    @staticmethod
    def _parse_weeks_to_str(weeks: List[str]) -> str:
        return reduce(lambda x, y: x + y, weeks)

    @staticmethod
    def _parse_date_to_str(date: date):
        return date.strftime("%Y-%m-%d") if date is not None else None

    @staticmethod
    def _parse_datetime_to_str(datetime: datetime):
        return datetime.strftime("%Y-%m-%d %H:%M:%S") if datetime is not None else None
