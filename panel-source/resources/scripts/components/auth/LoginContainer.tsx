import React, { useEffect, useRef, useState } from 'react';
import { Link, RouteComponentProps } from 'react-router-dom';
import login from '@/api/auth/login';
import LoginFormContainer from '@/components/auth/LoginFormContainer';
import { useStoreState } from 'easy-peasy';
import { Formik, FormikHelpers } from 'formik';
import { object, string } from 'yup';
import Field from '@/components/elements/Field';
import Button from '@/components/elements/Button';
import Reaptcha from 'reaptcha';
import useFlash from '@/plugins/useFlash';

interface Values {
    username: string;
    password: string;
}

const LoginContainer = ({ history }: RouteComponentProps) => {
    const ref = useRef<Reaptcha>(null);
    const [token, setToken] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const { clearFlashes, clearAndAddHttpError } = useFlash();
    const { enabled: recaptchaEnabled, siteKey } = useStoreState((state) => state.settings.data!.recaptcha);

    useEffect(() => {
        clearFlashes();
    }, []);

    const onSubmit = (values: Values, { setSubmitting }: FormikHelpers<Values>) => {
        clearFlashes();
        // If there is no token in the state yet, request the token and then abort this submit request
        // since it will be re-submitted when the recaptcha data is returned by the component.
        if (recaptchaEnabled && !token) {
            ref.current!.execute().catch((error) => {
                console.error(error);
                setSubmitting(false);
                clearAndAddHttpError({ error });
            });
            return;
        }

        login({ ...values, recaptchaData: token })
            .then((response) => {
                if (response.complete) {
                    // @ts-expect-error this is valid
                    window.location = response.intended || '/';
                    return;
                }
                history.replace('/auth/login/checkpoint', { token: response.confirmationToken });
            })
            .catch((error) => {
                console.error(error);
                setToken('');
                if (ref.current) ref.current.reset();
                setSubmitting(false);
                clearAndAddHttpError({ error });
            });
    };

    return (
        <Formik
            onSubmit={onSubmit}
            initialValues={{ username: '', password: '' }}
            validationSchema={object().shape({
                username: string().required('A username or email must be provided.'),
                password: string().required('Please enter your account password.'),
            })}
        >
            {({ isSubmitting, setSubmitting, submitForm }) => (
                <LoginFormContainer variant={'luxury'}>
                    <div className={'login-field-wrap'}>
                        <span className={'login-field-icon'} aria-hidden={'true'}>
                            <svg
                                width='18'
                                height='18'
                                viewBox='0 0 24 24'
                                fill='none'
                                stroke='currentColor'
                                strokeWidth='1.7'
                                strokeLinecap='round'
                                strokeLinejoin='round'
                            >
                                <circle cx='12' cy='8' r='4' />
                                <path d='M4 21a8 8 0 0 1 16 0' />
                            </svg>
                        </span>
                        <Field
                            id={'username'}
                            className={'login-input'}
                            type={'text'}
                            label={'Username or Email'}
                            name={'username'}
                            placeholder={'Enter your username or email'}
                            autoComplete={'username'}
                            disabled={isSubmitting}
                        />
                    </div>
                    <div className={'login-field-wrap'}>
                        <span className={'login-field-icon'} aria-hidden={'true'}>
                            <svg
                                width='18'
                                height='18'
                                viewBox='0 0 24 24'
                                fill='none'
                                stroke='currentColor'
                                strokeWidth='1.7'
                                strokeLinecap='round'
                                strokeLinejoin='round'
                            >
                                <rect x='4' y='10' width='16' height='11' rx='2' />
                                <path d='M8 10V7a4 4 0 1 1 8 0v3' />
                            </svg>
                        </span>
                        <Field
                            id={'password'}
                            className={'login-input'}
                            type={showPassword ? 'text' : 'password'}
                            label={'Password'}
                            name={'password'}
                            placeholder={'Enter your password'}
                            autoComplete={'current-password'}
                            disabled={isSubmitting}
                        />
                        <button
                            type={'button'}
                            className={'login-password-toggle'}
                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                            aria-pressed={showPassword}
                            onClick={() => setShowPassword((current) => !current)}
                        >
                            <svg
                                width='18'
                                height='18'
                                viewBox='0 0 24 24'
                                fill='none'
                                stroke='currentColor'
                                strokeWidth='1.7'
                                strokeLinecap='round'
                                strokeLinejoin='round'
                                aria-hidden={'true'}
                            >
                                <path d='M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z' />
                                <circle cx='12' cy='12' r='2.7' />
                                {showPassword && <path d='M4 4l16 16' />}
                            </svg>
                        </button>
                    </div>
                    <Button type={'submit'} size={'xlarge'} isLoading={isSubmitting} disabled={isSubmitting}>
                        Log In
                    </Button>
                    {recaptchaEnabled && (
                        <div className={'login-recaptcha'}>
                            <Reaptcha
                                ref={ref}
                                size={'invisible'}
                                sitekey={siteKey || '_invalid_key'}
                                onVerify={(response) => {
                                    setToken(response);
                                    submitForm();
                                }}
                                onExpire={() => {
                                    setSubmitting(false);
                                    setToken('');
                                }}
                            />
                        </div>
                    )}
                    <div className={'login-forgot'}>
                        <Link to={'/auth/password'}>Forgot password?</Link>
                    </div>
                </LoginFormContainer>
            )}
        </Formik>
    );
};

export default LoginContainer;
