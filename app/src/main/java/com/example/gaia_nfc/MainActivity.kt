package com.example.gaia_nfc

import android.content.Intent
import android.nfc.NdefMessage
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.Ndef
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import org.json.JSONObject
import java.io.IOException
import java.io.OutputStream
import java.net.Socket


class MainActivity : AppCompatActivity() {

    private val TAG = "MainActivity"

    private lateinit var nfcAdapter: NfcAdapter
    private lateinit var infoTextView: TextView

    private val httpClient = OkHttpClient()
    private lateinit var serverUrl: String

    private val SERVER_PORT = 8000 // Must match the Python script's port
    private val SERVER_IP = "127.0.0.1" // Will be forwarded by adb reverse

    private lateinit var statusText: TextView
    private lateinit var dataText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // Assumes you have a TextView with id `infoText`

        statusText = findViewById(R.id.status_text)
        dataText = findViewById(R.id.data_text)

        infoTextView = findViewById(R.id.infoText) // Make sure you have this ID in your layout
//        infoTextView.text = "Ready to scan an NFC tag.\n\nJSON data will be sent to the Python script."
        infoTextView.text = " "

        nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        if (nfcAdapter == null) {
            statusText.text = "NFC não é suportado neste dispositivo"
            return
        }

        if (!nfcAdapter.isEnabled) {
            statusText.text = "Por favor, ative o NFC nas configurações"
        } else {
            statusText.text = "Aproxime uma tag NFC"
        }


        serverUrl = "http://"+ SERVER_IP + ":" + SERVER_PORT + "/nfc-data"


        val testButton: Button = findViewById(R.id.button)
        testButton.setOnClickListener {
            val testJson = """{"id": "test001", "message": "Dados de teste", "value": 42}"""
            processNfcData(testJson)
        }

        handleIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        // Configurar foreground dispatch para capturar intents NFC
        val intent = Intent(this, javaClass).apply {
            addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        }

        val pendingIntent = android.app.PendingIntent.getActivity(
            this, 0, intent, android.app.PendingIntent.FLAG_MUTABLE
        )

        val techLists = arrayOf(arrayOf(Ndef::class.java.name))
        nfcAdapter.enableForegroundDispatch(this, pendingIntent, null, techLists)
    }

    override fun onPause() {
        super.onPause()
        nfcAdapter.disableForegroundDispatch(this)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

//    override fun onNewIntent(intent: Intent?) {
//        super.onNewIntent(intent)
//
//        // New: log and short toast to verify the method is reached
//        Log.d(TAG, "onNewIntent called: action=${intent?.action}")
//        runOnUiThread { Toast.makeText(this, "onNewIntent invoked", Toast.LENGTH_SHORT).show() }
//
//        if (intent?.action == NfcAdapter.ACTION_NDEF_DISCOVERED) {
//            Log.d(TAG, "NDEF_DISCOVERED received")
//            val rawMessages = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES)
//            if (rawMessages != null && rawMessages.isNotEmpty()) {
//                val firstMessage = rawMessages[0] as NdefMessage
//                val payloadBytes = firstMessage.records[0].payload
//
//                if (payloadBytes != null) {
//                    val payloadString = String(payloadBytes, Charsets.UTF_8)
//                    infoTextView.text = "NFC Tag Read:\n$payloadString"
//                    Log.d(TAG, "Tag payload: $payloadString")
//                    Toast.makeText(this, "Tag data read!", Toast.LENGTH_SHORT).show()
//                    sendDataToServer(payloadString)
//                } else {
//                    Log.d(TAG, "payloadBytes is null")
//                }
//            } else {
//                Log.d(TAG, "No NDEF messages in intent")
//            }
//        } else {
//            Log.d(TAG, "onNewIntent: action is not NDEF_DISCOVERED")
//        }
//    }
//

    private fun sendDataToServerHttp(jsonData: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val mediaType = "application/json; charset=utf-8".toMediaType()
                val body = RequestBody.create(mediaType, jsonData)
                val request = Request.Builder()
                    .url(serverUrl)
                    .post(body)
                    .build()

                val response = httpClient.newCall(request).execute()

                withContext(Dispatchers.Main) {
                    if (response.isSuccessful) {
                        statusText.text = "Dados enviados com sucesso!"
                        Toast.makeText(
                            this@MainActivity,
                            "Dados enviados para o servidor",
                            Toast.LENGTH_SHORT
                        ).show()
                    } else {
                        statusText.text = "Erro ao enviar dados: ${response.code}"
                        Toast.makeText(
                            this@MainActivity,
                            "Erro ao enviar dados: ${response.code}",
                            Toast.LENGTH_LONG
                        ).show()
                    }
                    response.close()
                }
            } catch (e: IOException) {
                withContext(Dispatchers.Main) {
                    statusText.text = "Erro de conexão com o servidor"
                    Toast.makeText(
                        this@MainActivity,
                        "Não foi possível conectar ao servidor. Verifique a conexão.",
                        Toast.LENGTH_LONG
                    ).show()
                    Log.e("NFC_READER", "Erro de conexão com o servidor", e)
                }
            }
        }
    }

    private fun sendDataToServerBySocket(data: String) {
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

    private fun handleIntent(intent: Intent) {
        val action = intent.action
        if (NfcAdapter.ACTION_NDEF_DISCOVERED == action ||
            NfcAdapter.ACTION_TAG_DISCOVERED == action ||
            NfcAdapter.ACTION_TECH_DISCOVERED == action
        ) {

            val rawMessages = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES)
            if (rawMessages != null && rawMessages.isNotEmpty()) {
                val firstMessage = rawMessages[0] as NdefMessage
                val payloadBytes = firstMessage.records[0].payload

                if (payloadBytes != null) {
                    val payloadString = String(payloadBytes, Charsets.UTF_8)
                    infoTextView.text = "NFC Tag Read:\n$payloadString"
                    Log.d(TAG, "Tag payload: $payloadString")
                    Toast.makeText(this, "Tag data read!", Toast.LENGTH_SHORT).show()

                    //  Enviando payload String Via Http
                    sendDataToServerHttp(payloadString)

                    // Enviando payload String Via Http
                    //sendDataToServerBySocket(payloadString)

                } else {
                    Log.d(TAG, "payloadBytes is null")
                }
            } else {
                Log.d(TAG, "No NDEF messages in intent")
            }

            val tag = intent.getParcelableExtra<Tag>(NfcAdapter.EXTRA_TAG)
            tag?.let {
                readNfcTag(it)
            }
        }
    }

    private fun readNfcTag(tag: Tag) {
        val ndef = Ndef.get(tag)
        if (ndef == null) {
            statusText.text = "Tag NFC não suportada ou não formatada"
            return
        }

        try {
            ndef.connect()
            val ndefMessage = ndef.ndefMessage
            if (ndefMessage != null) {
                val records = ndefMessage.records
                if (records.isNotEmpty()) {
                    val payload = records[0].payload
                    // Pular o header (primeiro byte) e converter para string
                    val jsonString = String(payload.copyOfRange(1, payload.size), Charsets.UTF_8)
                    processNfcData(jsonString)
                }
            } else {
                statusText.text = "Nenhuma mensagem NDEF encontrada na tag"
            }
        } catch (e: Exception) {
            statusText.text = "Erro ao ler tag NFC: ${e.message}"
            Log.e("NFC_READER", "Erro ao ler tag NFC", e)
        } finally {
            try {
                ndef.close()
            } catch (e: Exception) {
                Log.e("NFC_READER", "Erro ao fechar conexão NFC", e)
            }
        }
    }

    private fun processNfcData(jsonString: String) {
        runOnUiThread {
            statusText.text = "Dados NFC recebidos!"
            dataText.text = jsonString
        }

        // Validar se é um JSON válido
        try {
            JSONObject(jsonString) // Apenas para validação
            sendDataToServerHttp(jsonString)
        } catch (e: Exception) {
            runOnUiThread {
                statusText.text = "Erro: Dados não são JSON válido"
                Toast.makeText(this, "Dados NFC não são JSON válido", Toast.LENGTH_LONG).show()
            }
            Log.e("NFC_READER", "Dados não são JSON válido: $jsonString", e)
        }
    }
}
