package com.example.gaia_nfc

import android.content.Intent
import android.nfc.NdefMessage
import android.nfc.NfcAdapter
import android.os.Bundle
import android.util.Log
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.OutputStream
import java.net.Socket

class MainActivity : AppCompatActivity() {

    private val TAG = "MainActivity"

    private lateinit var nfcAdapter: NfcAdapter
    private lateinit var infoTextView: TextView
    private val SERVER_PORT = 8080 // Must match the Python script's port
    private val SERVER_IP = "127.0.0.1" // Will be forwarded by adb reverse

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // Assumes you have a TextView with id `infoText`

        infoTextView = findViewById(R.id.infoText) // Make sure you have this ID in your layout
        infoTextView.text = "Ready to scan an NFC tag.\n\nJSON data will be sent to the Python script."

        nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        if (!nfcAdapter.isEnabled) {
            Toast.makeText(this, "Please enable NFC.", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)

        // New: log and short toast to verify the method is reached
        Log.d(TAG, "onNewIntent called: action=${intent?.action}")
        runOnUiThread { Toast.makeText(this, "onNewIntent invoked", Toast.LENGTH_SHORT).show() }

        if (intent?.action == NfcAdapter.ACTION_NDEF_DISCOVERED) {
            Log.d(TAG, "NDEF_DISCOVERED received")
            val rawMessages = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES)
            if (rawMessages != null && rawMessages.isNotEmpty()) {
                val firstMessage = rawMessages[0] as NdefMessage
                val payloadBytes = firstMessage.records[0].payload

                if (payloadBytes != null) {
                    val payloadString = String(payloadBytes, Charsets.UTF_8)
                    infoTextView.text = "NFC Tag Read:\n$payloadString"
                    Log.d(TAG, "Tag payload: $payloadString")
                    Toast.makeText(this, "Tag data read!", Toast.LENGTH_SHORT).show()
                    sendDataToServer(payloadString)
                } else {
                    Log.d(TAG, "payloadBytes is null")
                }
            } else {
                Log.d(TAG, "No NDEF messages in intent")
            }
        } else {
            Log.d(TAG, "onNewIntent: action is not NDEF_DISCOVERED")
        }
    }

    private fun sendDataToServer(data: String) {
        // New: log and toast immediately to confirm invocation
        Log.d(TAG, "sendDataToServer called (data length=${data.length})")
        runOnUiThread { Toast.makeText(this, "sendDataToServer called", Toast.LENGTH_SHORT).show() }

        // Use Kotlin Coroutines for background network operation
        CoroutineScope(Dispatchers.IO).launch {
            try {
                Log.d(TAG, "Attempting to connect to $SERVER_IP:$SERVER_PORT")
                val socket = Socket(SERVER_IP, SERVER_PORT)
                val outputStream: OutputStream = socket.getOutputStream()
                outputStream.write(data.toByteArray(Charsets.UTF_8))
                outputStream.flush()
                socket.close()

                Log.d(TAG, "Data sent to server successfully")
                // Switch back to the Main thread to show a Toast
                withContext(Dispatchers.Main) {
                    Toast.makeText(applicationContext, "Data sent to Python script!", Toast.LENGTH_LONG).show()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Connection failed in sendDataToServer", e)
                e.printStackTrace()
                // Switch back to the Main thread to show an error Toast
                withContext(Dispatchers.Main) {
                    val errorMsg = "Connection failed. Is the Python server running?"
                    infoTextView.append("\n\n$errorMsg")
                    Toast.makeText(applicationContext, errorMsg, Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    // Also add this to your activity_main.xml layout file:
    // <TextView
    //     android:id="@+id/infoText"
    //     android:layout_width="wrap_content"
    //     android:layout_height="wrap_content"
    //     android:text="Ready..."
    //     app:layout_constraintBottom_toBottomOf="parent"
    //     app:layout_constraintEnd_toEndOf="parent"
    //     app:layout_constraintStart_toStartOf="parent"
    //     app:layout_constraintTop_toTopOf="parent" />
}
