package com.example.dataintegration.xml;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlElementWrapper;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "withdrawRequests")
public record WithdrawRequestsXmlDocument(
    @JacksonXmlProperty(localName = "withdrawRequest")
    @JacksonXmlElementWrapper(useWrapping = false)
    List<WithdrawRequestXmlEntry> requests
) {
    public List<String> enrollmentIds() {
        if (requests == null) {
            return List.of();
        }
        return requests.stream()
            .map(WithdrawRequestXmlEntry::enrollmentId)
            .filter(id -> id != null && !id.isBlank())
            .map(String::trim)
            .toList();
    }

    @JsonPropertyOrder({ "enrollmentId" })
    public record WithdrawRequestXmlEntry(String enrollmentId) {
    }
}
