import type { CollegeCode } from '../types/domain';

export const collegeLabels: Record<CollegeCode, string> = {
  A: '信息工程学院',
  B: '经济管理学院',
  C: '传媒设计学院',
};

const collegeTextLabels: Record<string, string> = {
  学院A: collegeLabels.A,
  学院B: collegeLabels.B,
  学院C: collegeLabels.C,
};

export function collegeLabel(code: CollegeCode) {
  return collegeLabels[code];
}

export function displayCollegeText(value: string) {
  return collegeTextLabels[value] ?? value;
}
