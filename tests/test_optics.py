import unittest
import numpy as np
from scipy.special import jn_zeros
import core as nl
import optics as O


class OpticsTests(unittest.TestCase):
    def test_matched_filter_normalizes_templates_and_fits_amplitude(self):
        data = np.array([1., -2., 3., -2.])
        templates = np.array([data, 10*data, -data, np.zeros_like(data)])
        score, amplitude = O.matched_filter(data, templates, np.ones(4))
        self.assertAlmostEqual(score[0], score[1])
        np.testing.assert_allclose(amplitude, [1., .1, 0., 0.])
        self.assertEqual(score[3], 0.)

    def test_spectral_budget_conserves_counts_and_uses_target_parameters(self):
        base = O.spectral_observation()
        np.testing.assert_allclose(base['e3']-base['e4'], base['signal'], atol=1e-8)
        np.testing.assert_allclose((base['e3']+base['e4']).sum(axis=1), sum(base['parts'].values()))
        self.assertGreater(base['snr'], 0.)
        larger = O.spectral_observation(planet_radius=2., exozodi=0., local_zodi=0.)
        np.testing.assert_allclose(larger['signal'], 4*base['signal'])
        np.testing.assert_allclose(larger['parts']['恒星漏光'], base['parts']['恒星漏光'])
        self.assertEqual(larger['parts']['外黄道光'].sum(), 0.)
        self.assertEqual(larger['parts']['本地黄道光'].sum(), 0.)

    def test_matrix_conserves_energy_and_matches_reference_dark_outputs(self):
        np.testing.assert_allclose(O.COMBINER @ O.COMBINER.conj().T, np.eye(4), atol=1e-15)
        x, y = np.meshgrid(np.linspace(-200, 200, 31)*nl.MAS2RAD, np.linspace(-200, 200, 31)*nl.MAS2RAD)
        response = O.response(x, y, 10e-6, 14.5, diffraction=False)
        np.testing.assert_allclose(response.sum(axis=0), 1, atol=1e-14)
        t3, t4 = nl.transmission(x, y, 10e-6, 7.25, 6.)
        np.testing.assert_allclose(response[2], t3, atol=1e-14)
        np.testing.assert_allclose(response[3], t4, atol=1e-14)
        self.assertLess(O.response(0., 0., 10e-6, 14.5)[2:].max(), 1e-15)

    def test_diffraction_envelope_and_first_zero(self):
        self.assertEqual(float(O.airy_amplitude(0., 0., 10e-6, 4.)), 1.)
        angle = jn_zeros(1, 1)[0]*10e-6/(np.pi*4)
        self.assertLess(float(O.airy_amplitude(angle, 0., 10e-6, 4.))**2, 1e-25)
        angles = np.linspace(0, 500, 101)*nl.MAS2RAD
        full = O.response(angles, angles, 10e-6, 14.5)
        airy = O.airy_amplitude(angles, angles, 10e-6, 4.)**2
        np.testing.assert_allclose(full.sum(axis=0), airy, atol=1e-14)

    def test_null_depth_uses_explicit_dark_to_bright_convention(self):
        self.assertEqual(O.two_beam_null(1., 0.), (0., 0.))
        self.assertAlmostEqual(O.two_beam_null(.8, 0.)[0], ((1-.8)/(1+.8))**2)

    def test_source_parameters_change_flux_without_changing_instrument_response(self):
        base = O.sky_experiment(npix=81)
        larger_planet = O.sky_experiment(npix=81, planet_radius=2.)
        np.testing.assert_array_equal(base['transfer'], larger_planet['transfer'])
        np.testing.assert_allclose(larger_planet['output']['行星'], 4*base['output']['行星'])
        dustier = O.sky_experiment(npix=81, exozodi=2.)
        np.testing.assert_array_equal(base['transfer'], dustier['transfer'])
        np.testing.assert_allclose(dustier['output']['外黄道光'], 2*base['output']['外黄道光'])
        self.assertGreater(base['stellar_counts'][2], 0.)
        for name in ['本地黄道光', '外黄道光']:
            rates = base['output'][name].sum(axis=(1, 2))
            self.assertLess(abs(rates[2]-rates[3]), max(rates[2], 1.)*1e-12)

    def test_zero_dust_and_finite_stellar_size(self):
        base = O.sky_experiment(npix=81, exozodi=0., local_zodi=0.)
        self.assertEqual(base['sky']['外黄道光'].sum(), 0.)
        self.assertEqual(base['sky']['本地黄道光'].sum(), 0.)
        larger_star = O.sky_experiment(npix=81, star_radius=2.)
        n1 = base['stellar_counts'][2]/base['stellar_flux']
        n2 = larger_star['stellar_counts'][2]/larger_star['stellar_flux']
        self.assertAlmostEqual(n2/n1, 4., delta=.02)


if __name__ == '__main__':
    unittest.main()
