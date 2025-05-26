package com.example.nll_sensortotext

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.card.MaterialCardView

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // 1) Toolbar를 ActionBar로 설정
        val toolbar = findViewById<MaterialToolbar>(R.id.topAppBar)
        setSupportActionBar(toolbar)

        // 2) MaterialCardView 참조
        val cardWifi = findViewById<MaterialCardView>(R.id.cardWifi)
        val cardSensorData = findViewById<MaterialCardView>(R.id.cardSensorData)
        val cardSensorRadiomap = findViewById<MaterialCardView>(R.id.cardSensorRadiomap)
        val cardArduino = findViewById<MaterialCardView>(R.id.cardArduino)

        // 3) 클릭 리스너 연결
        cardWifi.setOnClickListener {
            startActivity(Intent(this, Make_RadioMap::class.java))
        }

        cardSensorData.setOnClickListener {
            startActivity(Intent(this, SensorData::class.java))
        }

        cardSensorRadiomap.setOnClickListener {
            startActivity(Intent(this, Make_Sensor_RadioMap::class.java))
        }

        cardArduino.setOnClickListener {
            startActivity(Intent(this, ArduinoLoggingActivity::class.java))
        }
    }
}
