package com.example.dataintegration.integration;

import com.example.dataintegration.college.CollegeCode;

public record WithdrawalResult(
    String enrollmentId,
    boolean withdrawn,
    CollegeCode courseCollege
) {
}
