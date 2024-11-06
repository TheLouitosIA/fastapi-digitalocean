import React, { useState } from 'react';

const Inscription = () => {
  const [form, setForm] = useState({
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    marque_voiture: '',
    plaque_immatriculation: ''
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('http://localhost:8000/inscription/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });
    if (response.ok) {
      alert("Inscription réussie !");
    } else {
      alert("Erreur d'inscription.");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="nom" onChange={handleChange} placeholder="Nom" />
      <input name="prenom" onChange={handleChange} placeholder="Prénom" />
      <input name="email" type="email" onChange={handleChange} placeholder="Email" />
      <input name="telephone" onChange={handleChange} placeholder="Téléphone" />
      <input name="marque_voiture" onChange={handleChange} placeholder="Marque de la voiture" />
      <input name="plaque_immatriculation" onChange={handleChange} placeholder="Plaque d'immatriculation" />
      <button type="submit">S'inscrire</button>
    </form>
  );
};

export default Inscription;