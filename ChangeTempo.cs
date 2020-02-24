using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ChangeTempo : MonoBehaviour
{
    AudioSource m_MyAudioSource;
    bool m_Play;
    bool m_ToggleChange;

    public AudioMixer master;
    public string tempo = "Tempo";
    public string pitch_offset = "PitchOffset";

    void Start() {
      m_MyAudioSource = GetComponent<AudioSource>();
      m_Play = true;
    }

    void Update() {
      if(m_Play == true && m_ToggleChange == true)
      {
        master.SetFloat(tempo, )
        m_MyAudioSource.Play();
        m_ToggleChange = false;
      }
      if(m_Play == false && m_ToggleChange == true)
      {
        m_MyAudioSource.Stop();
        m_ToggleChange = false;
      }
    }

    void OnGUI()
    {
      m_Change = GUI.Toggle(new Rect(10, 10, 100, 60), m_Change, "Speed up");

      if(GUI.changed)
      {
        m_ToggleChange = true;
      }
    }
    public void NewTempo() {
      master.SetFloat("Tempo", 1.5f);
      master.SetFloat("PitchOffset", 1f/1.5f);
    }
}
