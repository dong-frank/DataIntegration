package com.example.dataintegration;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class DataIntegrationApplication {

    public static void main(String[] args) {
        SpringApplication.run(DataIntegrationApplication.class, args);
    }
}
